# memory_manager.py
from json_guardian import JSONGuardian

guardian = JSONGuardian()

def load_memory_block(name):
    file_path = guardian.memory_dir / f"{name}.json"
    guardian.validate_file(file_path)  # could be a lighter per-file check
    with open(file_path) as f:
        return json.load(f)

