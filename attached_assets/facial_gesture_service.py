import logging
import time
from typing import Dict, Optional, Tuple, List

import cv2
import mediapipe as mp
import numpy as np

logger = logging.getLogger(__name__)


class FacialGestureService:
    def __init__(self):
        """Initialize MediaPipe FaceMesh and configure logging."""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)
        self.fixation_start = None
        self.FIXATION_THRESHOLD = 2.0  # Seconds to confirm object focus
        self.eye_indices = {
            "left": [362, 385, 387, 263],
            "right": [33, 160, 158, 133],
        }
        logger.info("FacialGestureService initialized with MediaPipe FaceMesh")

    def detect_eye_movement(self, frame_data: bytes) -> Dict[str, any]:
        """Detect and analyze eye movements from a video frame.

        Args:
            frame_data: Raw bytes of the video frame

        Returns:
            Dictionary containing eye movement analysis results
        """
        try:
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                logger.error("Failed to decode frame data")
                return {"error": "Invalid frame data"}

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)

            if not results.multi_face_landmarks:
                return {"detected": False, "message": "No face detected"}

            h, w, _ = frame.shape
            analysis_results = []

            for face_landmarks in results.multi_face_landmarks:
                left_eye = [
                    (face_landmarks.landmark[i].x, face_landmarks.landmark[i].y)
                    for i in self.eye_indices["left"]
                ]
                right_eye = [
                    (face_landmarks.landmark[i].x, face_landmarks.landmark[i].y)
                    for i in self.eye_indices["right"]
                ]

                left_eye = np.array([(int(x * w), int(y * h)) for x, y in left_eye])
                right_eye = np.array([(int(x * w), int(y * h)) for x, y in right_eye])

                left_eye_center = np.mean(left_eye, axis=0).astype(int)
                right_eye_center = np.mean(right_eye, axis=0).astype(int)

                fixation_detected, fixation_duration = self._update_fixation()
                gaze_direction = self._estimate_gaze_direction(
                    left_eye_center, right_eye_center, w
                )

                analysis_results.append(
                    {
                        "left_eye_center": left_eye_center.tolist(),
                        "right_eye_center": right_eye_center.tolist(),
                        "fixation_detected": fixation_detected,
                        "fixation_duration": round(fixation_duration, 2),
                        "gaze_direction": gaze_direction,
                    }
                )

            return {
                "detected": True,
                "faces_detected": len(results.multi_face_landmarks),
                "analysis": analysis_results,
            }

        except Exception as e:
            logger.error(f"Error in eye movement detection: {str(e)}")
            return {"error": str(e)}

    def _update_fixation(self) -> Tuple[bool, float]:
        """Update fixation timer and determine if threshold is reached."""
        if self.fixation_start is None:
            self.fixation_start = time.time()
            return False, 0.0

        fixation_duration = time.time() - self.fixation_start
        if fixation_duration > self.FIXATION_THRESHOLD:
            self.fixation_start = None
            return True, fixation_duration
        return False, fixation_duration

    def _estimate_gaze_direction(
        self, left_center: np.ndarray, right_center: np.ndarray, frame_width: int
    ) -> str:
        """Estimate gaze direction based on average eye center position."""
        avg_x = (left_center[0] + right_center[0]) / 2
        if avg_x < 0.4 * frame_width:
            return "left"
        elif avg_x > 0.6 * frame_width:
            return "right"
        return "center"

    def cleanup(self):
        """Clean up MediaPipe resources."""
        if self.face_mesh:
            self.face_mesh.close()
