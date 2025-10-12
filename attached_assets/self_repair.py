# self_repair.py
import traceback
import os
import sys
import subprocess
import datetime

LOG_FILE = "self_repair.log"


def log_issue(error_msg):
    """Log error messages with timestamp for debugging history."""
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {error_msg}\n")
    print(f"[SELF-REPAIR] Logged issue: {error_msg}")


def run_with_repair(script, args=[]):
    """Run a Python script and attempt self-repair on failure."""
    try:
        subprocess.run([sys.executable, script] + args, check=True)
    except subprocess.CalledProcessError as e:
        log_issue(f"Runtime error in {script}: {str(e)}")
        analyze_and_patch(script, e)
    except Exception as e:
        log_issue(f"Unexpected error in {script}: {traceback.format_exc()}")
        analyze_and_patch(script, e)


def analyze_and_patch(script, error):
    """Very basic self-repair: detect common errors and attempt fixes."""
    error_str = str(error)

    if "ModuleNotFoundError" in error_str:
        missing_pkg = error_str.split("'")[1]
        print(f"[SELF-REPAIR] Missing package detected: {missing_pkg}")
        os.system(f"{sys.executable} -m pip install {missing_pkg}")

    elif "ImportError" in error_str and "cannot import name" in error_str:
        print("[SELF-REPAIR] Import conflict detected, check function defs.")
        # Could scan code for unused imports or rename clashes

    elif "cv2.error" in error_str:
        print("[SELF-REPAIR] OpenCV crash — likely imshow thread issue.")
        print("Suggest: move cv2.imshow to main thread.")

    elif "numpy" in error_str and "version" in error_str:
        print("[SELF-REPAIR] NumPy/TensorFlow mismatch.")
        print("Suggest: pin numpy==1.23.5 for TensorFlow compatibility.")

    else:
        print(f"[SELF-REPAIR] No automated fix. Error was: {error_str}")

    # Could extend to auto-edit scripts here, but safer to log + suggest
