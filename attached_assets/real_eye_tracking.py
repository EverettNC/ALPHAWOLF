"""
AlphaVox - Real Eye Tracking
-----------------------------------
This module provides actual webcam-based eye tracking for AlphaVox
instead of simulated data.
"""

import logging
import os
import threading
import time
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Screen regions for eye tracking
REGIONS = {
    "top_left": {"x": (0, 0.33), "y": (0, 0.33)},
    "top": {"x": (0.33, 0.66), "y": (0, 0.33)},
    "top_right": {"x": (0.66, 1.0), "y": (0, 0.33)},
    "left": {"x": (0, 0.33), "y": (0.33, 0.66)},
    "center": {"x": (0.33, 0.66), "y": (0.33, 0.66)},
    "right": {"x": (0.66, 1.0), "y": (0.33, 0.66)},
    "bottom_left": {"x": (0, 0.33), "y": (0.66, 1.0)},
    "bottom": {"x": (0.33, 0.66), "y": (0.66, 1.0)},
    "bottom_right": {"x": (0.66, 1.0), "y": (0.66, 1.0)},
}


class EyeTracking:
    """Service for real webcam-based eye tracking.

    Uses OpenCV and face/eye detection to track eye positions from a
    live webcam feed.
    """

    def __init__(self):
        self.is_tracking = False
        self.tracking_thread = None

        # Current eye position
        self.current_position = {"x": 0.5, "y": 0.5}
        self.current_region = "center"

        # Detected eye metrics
        self.left_eye = None
        self.right_eye = None
        self.face_found = False
        self.blink_detected = False
        self.last_blink_time = 0
        self.blink_count = 0

        # Load face and eye cascade classifiers
        try:
            # Try to load the built-in OpenCV cascade classifiers
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_eye.xml"
            )

            if self.face_cascade.empty() or self.eye_cascade.empty():
                logger.warning(
                    "Failed to load built-in cascade classifiers, using local files"
                )
                # Fall back to local files if built-in fails
                self.face_cascade = cv2.CascadeClassifier(
                    "models/haarcascade_frontalface_default.xml"
                )
                self.eye_cascade = cv2.CascadeClassifier("models/haarcascade_eye.xml")
        except Exception as e:
            logger.error(f"Error loading cascade classifiers: {e}")
            # Create directory for cascade files if needed
            os.makedirs("models", exist_ok=True)
            # We'll handle this gracefully by checking if the classifiers are valid before use

        # Initialize video capture
        self.cap = None
        self.frame_width = 640
        self.frame_height = 480

        # Tracking parameters
        self.min_face_size = (60, 60)
        self.eye_detect_interval = 0.1  # seconds
        self.last_detection_time = 0
        self.detection_count = 0

        # Debug parameters
        self.debug_mode = False
        self.debug_frame = None

        logger.info("Real eye tracking service initialized")

    def start_tracking(self) -> bool:
        """Start eye tracking using the webcam.

        Returns:
            bool: Whether tracking started successfully
        """
        if self.is_tracking:
            logger.warning("Eye tracking is already active")
            return False

        # Initialize video capture
        try:
            self.cap = cv2.VideoCapture(0)  # Try the default camera (index 0)
            if not self.cap.isOpened():
                logger.warning("Default camera failed, trying camera index 1")
                self.cap = cv2.VideoCapture(1)  # Try an alternative camera

            if not self.cap.isOpened():
                logger.error("Failed to open any camera")
                return False

            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)

            # Get actual frame size (may differ from requested)
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            logger.info(
                f"Camera initialized with frame size: {self.frame_width}x{self.frame_height}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            return False

        # Start tracking thread
        self.is_tracking = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()

        logger.info("Eye tracking started")
        return True

    def stop_tracking(self) -> bool:
        """Stop eye tracking.

        Returns:
            bool: Whether tracking was stopped successfully
        """
        if not self.is_tracking:
            logger.warning("Eye tracking is not active")
            return False

        self.is_tracking = False

        if self.tracking_thread:
            self.tracking_thread.join(timeout=1.0)

        if self.cap:
            self.cap.release()
            self.cap = None

        logger.info("Eye tracking stopped")
        return True

    def _tracking_loop(self):
        """Main eye tracking loop that runs in a background thread."""
        try:
            while self.is_tracking and self.cap:
                # Read a frame from the camera
                ret, frame = self.cap.read()

                if not ret or frame is None:
                    logger.warning("Failed to capture frame")
                    time.sleep(0.1)
                    continue

                # Mirror the frame horizontally for more intuitive display
                frame = cv2.flip(frame, 1)

                # Process the frame at a controlled interval
                current_time = time.time()
                if current_time - self.last_detection_time >= self.eye_detect_interval:
                    self.last_detection_time = current_time
                    self._process_frame(frame)
                    self.detection_count += 1

                # Store the frame for debug display if needed
                if self.debug_mode:
                    self.debug_frame = frame.copy()

                # Sleep to control processing rate
                time.sleep(0.01)

        except Exception as e:
            logger.error(f"Error in tracking loop: {e}")
            self.is_tracking = False

    def _process_frame(self, frame):
        """Process a video frame for eye tracking.

        Args:
            frame: Video frame to process
        """
        try:
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Check if face cascade is valid
            if self.face_cascade.empty():
                logger.error("Face cascade classifier is not loaded properly")
                return

            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=self.min_face_size
            )

            # Update face detection status
            self.face_found = len(faces) > 0

            # Process the largest face (assumed to be the user)
            if self.face_found:
                # Find the largest face by area
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = largest_face

                # Draw face rectangle in debug mode
                if self.debug_mode:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # Extract the face region
                face_roi = gray[y : y + h, x : x + w]

                # Detect eyes in the face region
                if self.eye_cascade.empty():
                    logger.error("Eye cascade classifier is not loaded properly")
                    return

                eyes = self.eye_cascade.detectMultiScale(
                    face_roi, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20)
                )

                # Clear previous eye detections
                self.left_eye = None
                self.right_eye = None

                # Process detected eyes
                if len(eyes) >= 2:
                    # Assume the leftmost eye in image coordinates is the right eye (mirrored)
                    # and the rightmost eye is the left eye
                    sorted_eyes = sorted(eyes, key=lambda e: e[0])

                    # Right eye (leftmost in image)
                    right_eye = sorted_eyes[0]
                    rx, ry, rw, rh = right_eye
                    self.right_eye = {
                        "x": x + rx + rw // 2,
                        "y": y + ry + rh // 2,
                        "width": rw,
                        "height": rh,
                    }

                    # Left eye (rightmost in image)
                    left_eye = sorted_eyes[1]
                    lx, ly, lw, lh = left_eye
                    self.left_eye = {
                        "x": x + lx + lw // 2,
                        "y": y + ly + lh // 2,
                        "width": lw,
                        "height": lh,
                    }

                    # Draw eye rectangles in debug mode
                    if self.debug_mode:
                        cv2.rectangle(
                            frame,
                            (x + rx, y + ry),
                            (x + rx + rw, y + ry + rh),
                            (0, 255, 0),
                            2,
                        )
                        cv2.rectangle(
                            frame,
                            (x + lx, y + ly),
                            (x + lx + lw, y + ly + lh),
                            (0, 255, 0),
                            2,
                        )

                    # Calculate normalized eye position (average of both eyes)
                    eye_x = (self.left_eye["x"] + self.right_eye["x"]) / 2
                    eye_y = (self.left_eye["y"] + self.right_eye["y"]) / 2

                    # Normalize coordinates to 0-1 range
                    norm_x = eye_x / self.frame_width
                    norm_y = eye_y / self.frame_height

                    # Update current position with some smoothing
                    self.current_position = {
                        "x": self.current_position["x"] * 0.7 + norm_x * 0.3,
                        "y": self.current_position["y"] * 0.7 + norm_y * 0.3,
                    }

                    # Determine the current region
                    self.current_region = self._get_region(
                        self.current_position["x"], self.current_position["y"]
                    )

                    # Check for blinks by analyzing eye aspect ratio
                    # This is a simplified detection - real implementation would be more sophisticated
                    if len(eyes) < 2 and self.left_eye and self.right_eye:
                        # If we previously had two eyes and now don't, it might be a blink
                        current_time = time.time()
                        if (
                            current_time - self.last_blink_time > 0.5
                        ):  # Prevent rapid consecutive blinks
                            self.blink_detected = True
                            self.blink_count += 1
                            self.last_blink_time = current_time
                            logger.debug("Blink detected")
                    else:
                        self.blink_detected = False

        except Exception as e:
            logger.error(f"Error processing frame: {e}")

    def _get_region(self, x: float, y: float) -> str:
        """Determine which screen region the coordinates fall into.

        Args:
            x: Normalized x-coordinate (0-1)
            y: Normalized y-coordinate (0-1)

        Returns:
            str: Region name
        """
        for region_name, region_bounds in REGIONS.items():
            x_min, x_max = region_bounds["x"]
            y_min, y_max = region_bounds["y"]

            if x_min <= x < x_max and y_min <= y < y_max:
                return region_name

        return "center"  # Default if no region matches

    def get_eye_position(self) -> Dict:
        """Get the current eye position and region.

        Returns:
            dict: Eye position information
        """
        return {
            "position": self.current_position,
            "region": self.current_region,
            "face_detected": self.face_found,
            "blink_detected": self.blink_detected,
            "blink_count": self.blink_count,
            "left_eye": self.left_eye,
            "right_eye": self.right_eye,
            "timestamp": time.time(),
        }

    def set_debug_mode(self, enable: bool) -> bool:
        """Enable or disable debug mode.

        In debug mode, the service will draw rectangles around detected faces and eyes
        on the debug frame.

        Args:
            enable: Whether to enable debug mode

        Returns:
            bool: Whether the mode was set successfully
        """
        self.debug_mode = enable
        logger.info(f"Debug mode {'enabled' if enable else 'disabled'}")
        return True

    def get_debug_frame(self) -> Optional[np.ndarray]:
        """Get the latest debug frame with annotations.

        Returns:
            numpy.ndarray or None: Debug frame with annotations, or None if not available
        """
        return self.debug_frame if self.debug_mode else None

    def process_camera_frame(self, frame):
        """Process a camera frame and add eye tracking visualization.

        Args:
            frame: Camera frame to process

        Returns:
            numpy.ndarray: Processed frame with visualization
        """
        if frame is None:
            return None

        # Make a copy to avoid modifying the original
        output_frame = frame.copy()

        # Add visualization elements
        if self.face_found:
            # Draw current position
            x = int(self.current_position["x"] * self.frame_width)
            y = int(self.current_position["y"] * self.frame_height)
            cv2.circle(output_frame, (x, y), 5, (0, 255, 255), -1)

            # Draw current region
            region = REGIONS[self.current_region]
            x1 = int(region["x"][0] * self.frame_width)
            y1 = int(region["y"][0] * self.frame_height)
            x2 = int(region["x"][1] * self.frame_width)
            y2 = int(region["y"][1] * self.frame_height)
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (255, 255, 0), 2)

            # Add text for current region
            cv2.putText(
                output_frame,
                f"Region: {self.current_region}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            # Add blink detection indicator
            if self.blink_detected:
                cv2.putText(
                    output_frame,
                    "BLINK!",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
        else:
            # No face detected
            cv2.putText(
                output_frame,
                "No face detected",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

        return output_frame


...

# Singleton instance
_real_eye_tracking_service = None


def get_real_eye_tracking_service():
    """Get the singleton instance of the real eye tracking service."""
    global _real_eye_tracking_service
    if _real_eye_tracking_service is None:
        _real_eye_tracking_service = EyeTracking()
    return _real_eye_tracking_service
