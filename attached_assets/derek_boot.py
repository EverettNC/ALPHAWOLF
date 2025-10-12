import yaml
import os

# Removed unused imports: datetime, Path
from memory_engine import MemoryEngine
from derek_autonomous_system import DerekAutonomousSystem


class DerekBoot:
    def __init__(self, manifest_path="derek_manifest.yaml"):
        self.manifest_path = manifest_path
        self.manifest = {}
        self.mode = None
        self.identity = None
        self.memory_path = None
        self.github_sync = False
        self.memory_engine = None
        self.system = None

    def load_manifest(self):
        print("[DEREK BOOT] Loading manifest...")
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError("Manifest file not found.")

        with open(self.manifest_path, "r") as f:
            self.manifest = yaml.safe_load(f)

        self.identity = self.manifest.get("identity", "Derek C")
        self.mode = self.manifest.get("active_mode", "engineer")
        self.memory_path = self.manifest.get("memory_path", "./memory/daily")
        self.github_sync = self.manifest.get("github_sync", False)

        print(f"[DEREK BOOT] Identity: {self.identity}")
        print(f"[DEREK BOOT] Active Mode: {self.mode}")
        print(f"[DEREK BOOT] Memory Source: {self.memory_path}")
        print(
            f"[DEREK BOOT] GitHub sync: {'ENABLED' if self.github_sync else 'DISABLED'}"
        )

    def initialize_memory(self):
        print("[DEREK BOOT] Initializing memory engine...")
        # If memory_path is a directory, point to the actual memory file
        if os.path.isdir(self.memory_path):
            memory_file = os.path.join(self.memory_path, "memory_store.json")
        else:
            memory_file = self.memory_path
        
        self.memory_engine = MemoryEngine(file_path=memory_file)
        self.memory_engine.load_memory()  # Correct method name
        print(f"[DEREK BOOT] MemoryEngine initialized using {memory_file}")

    def activate_system(self):
        print(f"[DEREK BOOT] Activating Derek system in '{self.mode}' mode...")
        # DerekAutonomousSystem initialized for learning and self-modification cycles
        # Note: safe_mode=False allows code modifications, set to True for read-only
        self.system = DerekAutonomousSystem(safe_mode=False)
        print(f"[DEREK BOOT] Autonomous system ready (mode: {self.mode})")

    def finalize(self):
        print("[DEREK BOOT] System initialized successfully. Derek is awake.")

    def run(self):
        self.load_manifest()
        self.initialize_memory()
        self.activate_system()
        self.finalize()


if __name__ == "__main__":
    boot = DerekBoot()
    boot.run()

