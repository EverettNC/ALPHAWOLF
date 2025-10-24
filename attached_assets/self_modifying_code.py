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
"""Self-Modifying Code Module for AlphaVox.

This module enables AlphaVox to modify its own code based on learning
and adaptation. It includes safety mechanisms to prevent catastrophic
changes and maintains backups of all modified files.
"""

import ast
import difflib
import importlib
import inspect
import json
import logging
import os
import re
import shutil
import sys
import threading
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests
from flask import Flask, jsonify, request

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("self_modifying_code")

# Check if Anthropic API key is available
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")


class SafetyError(Exception):
    """Exception raised for safety check failures."""

    pass


class CodeModification:
    def __init__(
        self,
        file_path: str,
        original_code: str,
        modified_code: str,
        description: str,
        modification_type: str,
        confidence: float,
    ):
        self.file_path = file_path
        self.original_code = original_code
        self.modified_code = modified_code
        self.description = description
        self.modification_type = modification_type
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()
        self.applied = False
        self.result = None

    def get_diff(self) -> str:
        orig_lines = self.original_code.splitlines(keepends=True)
        modified_lines = self.modified_code.splitlines(keepends=True)
        diff = difflib.unified_diff(
            orig_lines,
            modified_lines,
            fromfile=f"a/{self.file_path}",
            tofile=f"b/{self.file_path}",
            n=3,
        )
        return "".join(diff)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "description": self.description,
            "modification_type": self.modification_type,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "applied": self.applied,
            "result": self.result,
            "diff": self.get_diff(),
        }

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], original_code: str, modified_code: str
    ) -> "CodeModification":
        mod = cls(
            file_path=data["file_path"],
            original_code=original_code,
            modified_code=modified_code,
            description=data["description"],
            modification_type=data["modification_type"],
            confidence=data["confidence"],
        )
        mod.timestamp = data["timestamp"]
        mod.applied = data["applied"]
        mod.result = data["result"]
        return mod


class CodeModifier:
    def __init__(self, backup_dir: str = "data/backups"):
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)
        self.modifications = []
        self.load_modifications()
        self.min_confidence = 0.8
        self.max_lines_changed = 20
        self.safe_files = set()
        self._initialize_safe_files()

    def _initialize_safe_files(self):
        unsafe_patterns = [
            "main.py",
            ".git",
            "db.py",
            "pyproject.toml",
            "requirements.txt",
            "Pipfile",
            "setup.py",
            "self_modifying_code.py",
        ]
        key_directories = [".", "./modules", "./routes", "./attached_assets"]
        for directory in key_directories:
            if not os.path.exists(directory):
                continue
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        if not any(unsafe in file_path for unsafe in unsafe_patterns):
                            if file_path.startswith("./"):
                                file_path = file_path[2:]
                            self.safe_files.add(file_path)

    def load_modifications(self):
        path = os.path.join(self.backup_dir, "modification_history.json")
        if os.path.exists(path):
            try:
                with open(path) as f:
                    self.modifications = json.load(f)
            except json.JSONDecodeError:
                self.modifications = []

    def save_modifications(self):
        path = os.path.join(self.backup_dir, "modification_history.json")
        with open(path, "w") as f:
            json.dump(self.modifications, f, indent=2)

    def create_backup(self, file_path: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_name = f"{filename}.{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_name)
        shutil.copy2(file_path, backup_path)
        return backup_path

    def check_syntax(self, code: str) -> bool:
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def apply_modification(self, modification: CodeModification) -> bool:
        file_path = modification.file_path
        try:
            self._run_safety_checks(modification)
            backup_path = self.create_backup(file_path)
            with open(file_path, "w") as f:
                f.write(modification.modified_code)
            modification.applied = True
            modification.result = "success"
            self.modifications.append(modification.to_dict())
            self.save_modifications()
            return True
        except Exception as e:
            modification.applied = False
            modification.result = str(e)
            self.modifications.append(modification.to_dict())
            self.save_modifications()
            return False

    def _run_safety_checks(self, modification: CodeModification):
        file_path = modification.file_path
        if file_path not in self.safe_files:
            raise SafetyError(f"File {file_path} is not in the safe list")
        if modification.confidence < self.min_confidence:
            raise SafetyError("Confidence too low")
        if not self.check_syntax(modification.modified_code):
            raise SafetyError("Syntax error in modified code")
        changes = sum(
            1
            for a, b in zip(
                modification.original_code.splitlines(),
                modification.modified_code.splitlines(),
            )
            if a != b
        )
        changes += abs(
            len(modification.original_code.splitlines())
            - len(modification.modified_code.splitlines())
        )
        if changes > self.max_lines_changed:
            raise SafetyError("Too many lines changed")


class AICodeGenerator:
    def __init__(self):
        self.api_key = ANTHROPIC_API_KEY
        self.api_endpoint = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-5-sonnet-20241022"

    def generate_code_improvement(
        self, file_path: str, code: str, issue_description: str
    ) -> Tuple[str, str, float]:
        if not self.api_key:
            return self._fallback_code_generation(code, issue_description)

        prompt = f"""You are an expert Python developer helping to improve code for the AlphaVox AI system.

```python
{code}
```

The issue is: {issue_description}
"""

        try:
            headers = {
                "x-api-key": self.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01",
            }
            data = {
                "model": self.model,
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            response = requests.post(self.api_endpoint, headers=headers, json=data)
            result = response.json()
            content = result.get("content", [{}])[0].get("text", "")
            return (
                self._extract_code(content),
                self._extract_explanation(content),
                self._extract_confidence(content),
            )
        except Exception:
            return self._fallback_code_generation(code, issue_description)

    def _extract_code(self, content: str) -> str:
        match = re.search(r"```python\n(.*?)```", content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_explanation(self, content: str) -> str:
        return content.split("```")[-1].strip()

    def _extract_confidence(self, content: str) -> float:
        match = re.search(r"confidence[:\s]+(\d+\.\d+)", content.lower())
        return float(match.group(1)) if match else 0.7

    def _fallback_code_generation(
        self, code: str, issue_description: str
    ) -> Tuple[str, str, float]:
        return code, "Fallback code generation used", 0.6


class SelfModifyingCodeEngine:
    def __init__(self):
        self.code_modifier = CodeModifier()
        self.ai_generator = AICodeGenerator()
        self.modification_queue = []
        self.modification_lock = threading.Lock()
        self.auto_mode_active = False
        self.auto_thread = None
        self.pending_issues = []

    def queue_modification(
        self, file_path: str, issue_description: str, modification_type: str = "bugfix"
    ) -> bool:
        if not os.path.exists(file_path):
            return False
        with self.modification_lock:
            self.modification_queue.append(
                {
                    "file_path": file_path,
                    "issue_description": issue_description,
                    "modification_type": modification_type,
                }
            )
            return True

    def process_queue(self, auto_mode: bool = False) -> List[Dict[str, Any]]:
        results = []
        with self.modification_lock:
            queue_copy = self.modification_queue[:]
            self.modification_queue.clear()
        for item in queue_copy:
            try:
                with open(item["file_path"]) as f:
                    original = f.read()
                modified, explanation, confidence = (
                    self.ai_generator.generate_code_improvement(
                        item["file_path"], original, item["issue_description"]
                    )
                )
                modification = CodeModification(
                    item["file_path"],
                    original,
                    modified,
                    explanation,
                    item["modification_type"],
                    confidence,
                )
                status = (
                    "applied"
                    if auto_mode
                    and confidence >= self.code_modifier.min_confidence
                    and self.code_modifier.apply_modification(modification)
                    else "generated"
                )
                results.append(
                    {
                        "file_path": item["file_path"],
                        "status": status,
                        "confidence": confidence,
                        "description": item["issue_description"],
                        "diff": modification.get_diff(),
                    }
                )
            except Exception as e:
                results.append(
                    {"file_path": item["file_path"], "status": "error", "error": str(e)}
                )
        return results

    def start_auto_mode(self):
        if not self.auto_mode_active:
            self.auto_mode_active = True
            self.auto_thread = threading.Thread(target=self._auto_mode_loop)
            self.auto_thread.daemon = True
            self.auto_thread.start()

    def stop_auto_mode(self):
        self.auto_mode_active = False
        if self.auto_thread:
            self.auto_thread.join(timeout=5.0)

    def _auto_mode_loop(self):
        while self.auto_mode_active:
            if self.pending_issues:
                for issue in self.pending_issues[:5]:
                    self.queue_modification(
                        issue["module"], issue["description"], "bugfix"
                    )
                self.pending_issues = self.pending_issues[5:]
            if self.modification_queue:
                self.process_queue(auto_mode=True)
            time.sleep(300)


self_modifying_code_engine = SelfModifyingCodeEngine()


def get_self_modifying_code_engine():
    return self_modifying_code_engine


# Flask app integration route
app = Flask(__name__)


@app.route("/mod/queue", methods=["POST"])
def mod_queue():
    data = request.json
    engine = get_self_modifying_code_engine()
    success = engine.queue_modification(
        file_path=data["file"],
        issue_description=data["issue"],
        modification_type=data.get("type", "bugfix"),
    )
    return jsonify({"queued": success})


# AlphaVox boot integration
try:
    get_self_modifying_code_engine().start_auto_mode()
except Exception as e:
    logger.error(f"Failed to start auto mode: {e}")
