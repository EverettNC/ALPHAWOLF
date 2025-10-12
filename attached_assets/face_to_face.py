# face_to_face.py
import cv2
import threading
import time

# Avatar images
idle = cv2.imread("avatar_idle.png")
talking = cv2.imread("avatar_talking.png")

if idle is None or talking is None:
    print("[WARN] Avatar images not found, using blank placeholders")
    idle = 255 * np.ones((400, 400, 3), dtype=np.uint8)
    talking = idle.copy()

# Try to import DeepFace
deepface_available = False
try:
    from deepface import DeepFace

    deepface_available = True
    print("[INFO] DeepFace loaded successfully.")
except Exception as e:
    print(f"[WARN] DeepFace unavailable: {e}")
    print("[INFO] Running in avatar-only mode.")

# Webcam loop


def webcam_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot access webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        # If DeepFace is available, run analysis
        if deepface_available:
            try:
                result = DeepFace.analyze(
                    frame, actions=["emotion"], enforce_detection=False
                )
                dominant = result[0]["dominant_emotion"]
                cv2.putText(
                    frame,
                    f"Emotion: {dominant}",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )
            except Exception as e:
                cv2.putText(
                    frame,
                    f"DeepFace error: {str(e)}",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

        cv2.imshow("DerekC Face-to-Face", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


# Avatar loop


def avatar_loop():
    state = "idle"
    while True:
        if state == "idle":
            frame = idle.copy()
        else:
            frame = talking.copy()

        cv2.imshow("DerekC Avatar", frame)
        if cv2.waitKey(500) & 0xFF == ord("q"):
            break
        state = "talking" if state == "idle" else "idle"


if __name__ == "__main__":
    threading.Thread(target=webcam_loop, daemon=True).start()
    avatar_loop()
