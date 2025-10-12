# json_guardian.py
import json
import jsonschema
from pathlib import Path

from jsonschema import validate

class JSONGuardian:
    def __init__(self, schema_dir="schemas", memory_dir="memory"):
        self.schema_dir = Path(schema_dir)
        self.memory_dir = Path(memory_dir)

    def validate_all(self):
        for file in self.memory_dir.rglob("*.json"):
            schema_file = self.schema_dir / f"{file.stem}_schema.json"
            if not schema_file.exists():
                raise FileNotFoundError(f"No schema for {file.name}")
            with open(file) as f, open(schema_file) as s:
                data = json.load(f)
                schema = json.load(s)
                validate(instance=data, schema=schema)

