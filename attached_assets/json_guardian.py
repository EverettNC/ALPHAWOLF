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

