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
"""Self-Learning and Adaptation Engine for AlphaWolf.

Part of The Christman AI Project - Powered by LumaCognify AI
Originally developed for AlphaVox, adapted for AlphaWolf's cognitive care mission.

This module implements autonomous learning capabilities for AlphaWolf,
allowing the system to improve over time based on user interactions,
adapt its models for dementia and Alzheimer's care, and continuously
enhance its ability to support patients and caregivers.

Mission: Cognitive support that learns, adapts, and never forgets to care.
"""

import ast
import importlib
import inspect
import json
import logging
import os
import re
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from openai import OpenAI
from memory_engine import MemoryEngine

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
memory_engine = MemoryEngine(file_path="./memory/memory_store.json")
 

# Ensure persistent data directories exist
os.makedirs("data/learning", exist_ok=True)
os.makedirs("data/backups", exist_ok=True)

# Setup logging for the AI learning engine
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_learning_engine")


class CodeAnalyzer:
    """Analyzes code structure and identifies potential improvements."""

    def __init__(self):
        self.function_stats = {}
        self.error_patterns = {}
        self.load_error_patterns()

    def load_error_patterns(self):
        """Load known error patterns from a database or file."""
        # In a real implementation, this would load from the database
        self.error_patterns = {
            "circular_import": {
                "pattern": r"ImportError: cannot import name .+ from .+ circular import",
                "solution": "Restructure modules to avoid circular dependencies",
            },
            "attribute_error": {
                "pattern": r"AttributeError: .+ has no attribute .+",
                "solution": "Check if the object is properly initialized and the attribute exists",
            },
            "index_error": {
                "pattern": r"IndexError: .+",
                "solution": "Verify array bounds and add boundary checks",
            },
            "key_error": {
                "pattern": r"KeyError: .+",
                "solution": "Add key existence check with .get() or try/except",
            },
            "type_error": {
                "pattern": r"TypeError: .+",
                "solution": "Add type checking or conversion",
            },
        }

    def analyze_module(self, module_path: str) -> Dict[str, Any]:
        """Analyze a Python module for potential improvements."""
        with open(module_path, "r") as file:
            content = file.read()

        tree = ast.parse(content)
        functions = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = {
                    "lineno": node.lineno,
                    "args": len(node.args.args),
                    "complexity": self._calculate_complexity(node),
                    "docstring": ast.get_docstring(node) is not None,
                }

        return {
            "functions": functions,
            "imports": self._extract_imports(tree),
            "global_vars": self._extract_globals(tree),
        }

    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for subnode in ast.walk(node):
            if isinstance(subnode, (ast.If, ast.While, ast.For, ast.And, ast.Or)):
                complexity += 1
            elif isinstance(subnode, ast.Try):
                complexity += len(subnode.handlers)

        return complexity

    def _extract_imports(self, tree) -> List[str]:
        """Extract import statements from AST."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for name in node.names:
                    imports.append(f"{module}.{name.name}")

        return imports

    def _extract_globals(self, tree) -> List[str]:
        """Extract global variables from AST."""
        globals_list = []

        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        globals_list.append(target.id)

        return globals_list

    def check_for_errors(self, error_log: str) -> List[Dict[str, Any]]:
        """Analyze error logs for patterns and suggest fixes."""
        findings = []

        for error_type, error_info in self.error_patterns.items():
            matches = re.finditer(error_info["pattern"], error_log)
            for match in matches:
                findings.append(
                    {
                        "type": error_type,
                        "match": match.group(0),
                        "solution": error_info["solution"],
                    }
                )

        return findings


class ModelOptimizer:
    """Optimizes models based on usage patterns and interaction data."""

    def __init__(self, data_dir: str = "data/learning"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.interaction_stats = self._load_stats()
        self.learning_rate = 0.1  # How quickly the model adapts

    def _load_stats(self) -> Dict[str, Any]:
        """Load interaction statistics from file."""
        stats_file = os.path.join(self.data_dir, "model_stats.json")

        if os.path.exists(stats_file):
            try:
                with open(stats_file, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                logger.warning("Failed to load model stats, starting fresh")

        # Default empty stats structure
        return {
            "intents": {},
            "gestures": {},
            "symbols": {},
            "user_preferences": {},
            "success_rate": {},
            "last_updated": datetime.now().isoformat(),
        }

    def save_stats(self):
        """Save current statistics to file."""
        stats_file = os.path.join(self.data_dir, "model_stats.json")
        self.interaction_stats["last_updated"] = datetime.now().isoformat()

        with open(stats_file, "w") as file:
            json.dump(self.interaction_stats, file, indent=2)

    def record_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """Record a user interaction for learning."""
        # Get the appropriate stats section
        if interaction_type == "text":
            section = "intents"
            key = data.get("intent")
        elif interaction_type == "gesture":
            section = "gestures"
            key = data.get("gesture")
        elif interaction_type == "symbol":
            section = "symbols"
            key = data.get("symbol")
        else:
            logger.warning(f"Unknown interaction type: {interaction_type}")
            return

        # Record the interaction
        if key:
            if key not in self.interaction_stats[section]:
                self.interaction_stats[section][key] = {
                    "count": 0,
                    "success": 0,
                    "confidence_sum": 0,
                    "last_used": None,
                }

            stats = self.interaction_stats[section][key]
            stats["count"] += 1
            stats["last_used"] = datetime.now().isoformat()

            # If confidence provided, update stats
            if "confidence" in data:
                stats["confidence_sum"] += float(data["confidence"])

            # If user feedback provided, update success
            if "success" in data:
                stats["success"] += 1 if data["success"] else 0

        # Save after each significant interaction
        if self.interaction_stats[section].get(key, {}).get("count", 0) % 10 == 0:
            self.save_stats()

    def optimize_models(self):
        """Run optimization on models based on collected data."""
        # Analyze intent distribution
        intent_distribution = self._analyze_distribution("intents")
        gesture_distribution = self._analyze_distribution("gestures")
        symbol_distribution = self._analyze_distribution("symbols")

        # Generate model updates
        model_updates = {
            "intents": self._generate_intent_updates(intent_distribution),
            "gestures": self._generate_gesture_updates(gesture_distribution),
            "symbols": self._generate_symbol_updates(symbol_distribution),
        }

        # Log the suggested updates
        logger.info(
            f"Model optimization generated updates: {json.dumps(model_updates, indent=2)}"
        )

        return model_updates

    def _analyze_distribution(self, section: str) -> Dict[str, Dict[str, float]]:
        """Analyze usage distribution for a section of data."""
        items = self.interaction_stats.get(section, {})
        total_count = sum(item.get("count", 0) for item in items.values())

        distribution = {}
        for key, stats in items.items():
            count = stats.get("count", 0)
            if total_count > 0:
                frequency = count / total_count
            else:
                frequency = 0

            success_rate = 0
            if count > 0:
                success_rate = stats.get("success", 0) / count

            avg_confidence = 0
            if count > 0:
                avg_confidence = stats.get("confidence_sum", 0) / count

            distribution[key] = {
                "frequency": frequency,
                "success_rate": success_rate,
                "avg_confidence": avg_confidence,
                "count": count,
            }

        return distribution

    def _generate_intent_updates(
        self, distribution: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Generate updates for intent recognition based on distribution."""
        updates = {}

        # Identify high-frequency, low-confidence intents
        for intent, stats in distribution.items():
            if stats["count"] > 10 and stats["avg_confidence"] < 0.7:
                updates[intent] = {
                    "boost_confidence": min(0.1, 0.7 - stats["avg_confidence"]),
                    "reason": "High frequency but low confidence",
                }

        return updates

    def _generate_gesture_updates(
        self, distribution: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Generate updates for gesture recognition based on distribution."""
        updates = {}

        # Similar logic for gestures
        for gesture, stats in distribution.items():
            if stats["count"] > 5 and stats["success_rate"] < 0.6:
                updates[gesture] = {
                    "improve_recognition": True,
                    "reason": "Low success rate for common gesture",
                }

        return updates

    def _generate_symbol_updates(
        self, distribution: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Generate updates for symbol mapping based on distribution."""
        updates = {}

        # Find most/least used symbols
        items = sorted(distribution.items(), key=lambda x: x[1]["count"], reverse=True)

        # Suggest updates for rarely used symbols with low success
        for symbol, stats in distribution.items():
            if stats["count"] < 3 and stats["success_rate"] < 0.5:
                updates[symbol] = {
                    "review_mapping": True,
                    "reason": "Rarely used with low success",
                }

        return updates


class SelfImprovementEngine:
    """
    Engine that coordinates autonomous learning and self-improvement:
    1. Monitors system performance
    2. Collects usage statistics
    3. Identifies potential improvements
    4. Implements safe changes autonomously
    """

    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.model_optimizer = ModelOptimizer()
        self.learning_active = False
        self.learning_thread = None
        self.error_logs = []
        self.improvement_suggestions = []
        self.last_optimization = datetime.now() - timedelta(days=1)
        self.optimization_interval = timedelta(hours=1)

        # Create required directories
        os.makedirs("data/learning", exist_ok=True)
        os.makedirs("data/backups", exist_ok=True)

    def start_learning(self):
        """Start the autonomous learning process."""
        if not self.learning_active:
            self.learning_active = True
            self.learning_thread = threading.Thread(target=self._learning_loop)
            self.learning_thread.daemon = True
            self.learning_thread.start()
            logger.info("Self-improvement engine started")
            return True
        return False

    def stop_learning(self):
        """Stop the autonomous learning process."""
        if self.learning_active:
            self.learning_active = False
            if self.learning_thread:
                self.learning_thread.join(timeout=5.0)
            logger.info("Self-improvement engine stopped")
            return True
        return False

    def _learning_loop(self):
        """Main learning loop that runs continuously."""
        while self.learning_active:
            try:
                # Perform learning tasks
                self._collect_performance_metrics()

                # Run optimization at specified intervals
                if datetime.now() - self.last_optimization > self.optimization_interval:
                    self._optimize_system()
                    self.last_optimization = datetime.now()

                # Analyze error logs
                self._analyze_errors()

                # Sleep to prevent excessive CPU usage
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in learning loop: {str(e)}")
                time.sleep(300)  # Longer sleep on error

    def _collect_performance_metrics(self):
        """Collect system performance metrics."""
        # This would monitor memory usage, response times, etc.
        # For now, just log that we're collecting metrics
        logger.debug("Collecting performance metrics")

    def _optimize_system(self):
        """Run system optimization routines."""
        logger.info("Running system optimization")

        # Optimize models
        updates = self.model_optimizer.optimize_models()

        # Analyze code
        core_modules = [
            "app.py",
            "models.py",
            "nonverbal_engine.py",
            "eye_tracking_service.py",
            "sound_recognition_service.py",
        ]

        for module in core_modules:
            if os.path.exists(module):
                try:
                    analysis = self.code_analyzer.analyze_module(module)
                    self._process_code_analysis(module, analysis)
                except Exception as e:
                    logger.error(f"Error analyzing {module}: {str(e)}")

    def _process_code_analysis(self, module: str, analysis: Dict[str, Any]):
        """Process results of code analysis."""
        # Look for complex functions
        for func_name, stats in analysis.get("functions", {}).items():
            if stats.get("complexity", 0) > 10:
                self.improvement_suggestions.append(
                    {
                        "module": module,
                        "function": func_name,
                        "issue": "high_complexity",
                        "description": f"Function has high complexity ({stats['complexity']})",
                        "severity": "medium",
                    }
                )

            # Check for missing docstrings
            if not stats.get("docstring", False) and stats.get("args", 0) > 1:
                self.improvement_suggestions.append(
                    {
                        "module": module,
                        "function": func_name,
                        "issue": "missing_docstring",
                        "description": "Function with multiple arguments has no docstring",
                        "severity": "low",
                    }
                )

        # Save the suggestions
        self._save_suggestions()

    def _analyze_errors(self):
        """Analyze recorded errors and suggest improvements."""
        if not self.error_logs:
            return

        for error in self.error_logs:
            findings = self.code_analyzer.check_for_errors(error)

            for finding in findings:
                self.improvement_suggestions.append(
                    {
                        "module": "unknown",  # Would be extracted from error
                        "issue": finding["type"],
                        "description": finding["match"],
                        "solution": finding["solution"],
                        "severity": "high",
                    }
                )

        # Clear processed errors
        self.error_logs = []

        # Save the suggestions
        self._save_suggestions()

    def _save_suggestions(self):
        """Save improvement suggestions to file."""
        if not self.improvement_suggestions:
            return

        suggestions_file = "data/learning/improvement_suggestions.json"

        # Load existing suggestions
        existing = []
        if os.path.exists(suggestions_file):
            try:
                with open(suggestions_file, "r") as file:
                    existing = json.load(file)
            except json.JSONDecodeError:
                pass

        # Add timestamp to new suggestions
        timestamp = datetime.now().isoformat()
        for suggestion in self.improvement_suggestions:
            suggestion["timestamp"] = timestamp
            existing.append(suggestion)

        # Save back to file
        with open(suggestions_file, "w") as file:
            json.dump(existing, file, indent=2)

        # Clear after saving
        self.improvement_suggestions = []

    def register_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """Register user interaction for learning."""
        self.model_optimizer.record_interaction(interaction_type, data)

    def register_error(self, error_log: str):
        """Register an error for analysis."""
        self.error_logs.append(error_log)

    def get_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Get current improvement suggestions."""
        suggestions_file = "data/learning/improvement_suggestions.json"

        if os.path.exists(suggestions_file):
            try:
                with open(suggestions_file, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return []
        return []

    def self_test(self):
        """Run basic self‑improvement engine tests."""
        print("=== SelfImprovementEngine Self‑Test ===")
        # Test model optimizer
        updates = self.model_optimizer.optimize_models()
        print("Model updates:", updates)
        # Test code analyzer on this module
        analysis = self.code_analyzer.analyze_module(__file__)
        print("Code analysis functions:", list(analysis.get("functions", {}).keys()))
        # Test error analysis
        self.register_error("AttributeError: dummy has no attribute x")
        self._analyze_errors()
        print("Improvement suggestions:", self.get_improvement_suggestions())
        print("=== Self‑Test Complete ===")


# Initialize the global self-improvement engine
self_improvement_engine = SelfImprovementEngine()


# Utility function to get the engine instance
def get_self_improvement_engine():
    return self_improvement_engine


# --- Compatibility wrapper for AlphaWolf's brain (Derek C integration) ---
_engine_instance = None


def learn_from_text(text: str):
    """
    Directly embed crawled text and store in AlphaWolf's memory engine.
    This allows AlphaWolf to learn from research, caregiver tips, and
    dementia care best practices to continuously improve patient support.
    
    Originally designed for Derek C's knowledge acquisition system.
    """
    if not text or not text.strip():
        logger.warning("Received empty text for learning.")
        return "No text provided"

    try:
        emb = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        vector = emb.data[0].embedding
        memory_engine.save({
            "type": "web_ingest",
            "text": text,
            "vector": vector,
            "source": "alphawolf_learning"
        })
        logger.info(f"✅ AlphaWolf learned from {len(text)} characters of text")
        return "Learning complete"
    except Exception as e:
        logger.error(f"❌ AlphaWolf learning failed: {e}")
        return "Learning failed"

if __name__ == "__main__":
    print("Running SelfImprovementEngine self‑test")
    self_improvement_engine.self_test()
