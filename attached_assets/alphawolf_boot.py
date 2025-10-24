# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com
import yaml
import os

# Removed unused imports: datetime, Path
from memory_engine import MemoryEngine
from alphawolf_autonomous_system import alphawolfAutonomousSystem


class AlphaWolfBoot:
    def __init__(self, manifest_path="alphawolf_manifest.yaml"):
        self.manifest_path = manifest_path
        self.manifest = {}
        self.mode = None
        self.identity = None
        self.memory_path = None
        self.github_sync = False
        self.memory_engine = None
        self.system = None

    def load_manifest(self):
        print("[ALPHAWOLF BOOT] Loading manifest...")
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError("Manifest file not found.")

        with open(self.manifest_path, "r") as f:
            self.manifest = yaml.safe_load(f)

        self.identity = self.manifest.get("identity", "AlphaWolf")
        self.mode = self.manifest.get("active_mode", "engineer")
        self.memory_path = self.manifest.get("memory_path", "./memory/daily")
        self.github_sync = self.manifest.get("github_sync", False)

        print(f"[ALPHAWOLF BOOT] Identity: {self.identity}")
        print(f"[ALPHAWOLF BOOT] Active Mode: {self.mode}")
        print(f"[ALPHAWOLF BOOT] Memory Source: {self.memory_path}")
        print(
            f"[ALPHAWOLF BOOT] GitHub sync: {'ENABLED' if self.github_sync else 'DISABLED'}"
        )

    def initialize_memory(self):
        print("[ALPHAWOLF BOOT] Initializing memory engine...")
        # If memory_path is a directory, point to the actual memory file
        if os.path.isdir(self.memory_path):
            memory_file = os.path.join(self.memory_path, "memory_store.json")
        else:
            memory_file = self.memory_path
        
        self.memory_engine = MemoryEngine(file_path=memory_file)
        self.memory_engine.load_memory()  # Correct method name
        print(f"[ALPHAWOLF BOOT] MemoryEngine initialized using {memory_file}")

    def activate_system(self):
        print(f"[ALPHAWOLF BOOT] Activating AlphaWolf system in '{self.mode}' mode...")
        # AlphaWolfAutonomousSystem initialized for learning and self-modification cycles
        # Note: safe_mode=False allows code modifications, set to True for read-only
        self.system = alphawolfAutonomousSystem(safe_mode=False)
        print(f"[ALPHAWOLF BOOT] Autonomous system ready (mode: {self.mode})")

    def finalize(self):
        print("[ALPHAWOLF BOOT] System initialized successfully. AlphaWolf is awake.")

    def run(self):
        self.load_manifest()
        self.initialize_memory()
        self.activate_system()
        self.finalize()


if __name__ == "__main__":
    boot = AlphaWolfBoot()
    boot.run()

