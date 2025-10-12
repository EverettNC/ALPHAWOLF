# vision_engine.py
import cv2
from deepface import DeepFace
import threading

try:
    import cv2
    from deepface import DeepFace
except ImportError as e:
    print(f"[Vision] Dependency missing: {e}")

class VisionEngine:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            print("Vision engine already running.")
            return
        self.running = True
        self.thread = threading.Thread(target=self._vision_loop, daemon=True)
        self.thread.start()
        print("👁️  Vision engine started.")

    def stop(self):
        self.running = False
        print("👁️  Vision engine stopped.")

    def _vision_loop(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print("[ERROR] Could not access webcam.")
            self.running = False
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            try:
                result = DeepFace.analyze(
                    frame, actions=["emotion"], enforce_detection=False
                )
                dominant = result[0]["dominant_emotion"]
                cv2.putText(
                    frame, f"Emotion: {dominant}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
                )
            except Exception:
                cv2.putText(
                    frame, "Emotion: Unknown", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
                )

            cv2.imshow("Everett Cam", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.running = False


if __name__ == "__main__":
    vision_loop()
