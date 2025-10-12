"""
Configuration Management for Derek Dashboard
The Christman AI Project
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class Settings:
    """Central configuration for Derek Dashboard"""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    CONFIG_DIR = PROJECT_ROOT / "config"
    DATA_DIR = PROJECT_ROOT / "data"
    MODELS_DIR = PROJECT_ROOT / "models"
    LOGS_DIR = PROJECT_ROOT / "logs"
    MEDIA_DIR = PROJECT_ROOT / "media"
    KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "data" / "knowledge_base"

    # Identity configuration
    IDENTITY_FILE = CONFIG_DIR / "derek_identity.json"
    LEARNING_CHAMBERS_FILE = CONFIG_DIR / "learning_chambers.json"

    # Self-modification logs
    SELF_MODIFICATION_LOG_DIR = PROJECT_ROOT / "logs" / "self_modifications"

    # API Configuration
    API_HOST = os.getenv("DEREK_API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("DEREK_API_PORT", "8000"))
    API_DEBUG = os.getenv("DEREK_API_DEBUG", "false").lower() == "true"

    # AI Model Configuration
    ML_MODEL_PATH = MODELS_DIR / "derek_ml_model.pkl"
    NLP_MODEL = "en_core_web_sm"  # spaCy model
    LLM_MODEL = "claude-sonnet-4"  # Default LLM

    # Service Configuration
    ENABLE_VOICE = os.getenv("ENABLE_VOICE", "true").lower() == "true"
    ENABLE_VISION = os.getenv("ENABLE_VISION", "true").lower() == "true"
    ENABLE_MEMORY = os.getenv("ENABLE_MEMORY", "true").lower() == "true"
    ENABLE_EMOTION = os.getenv("ENABLE_EMOTION", "true").lower() == "true"

    # Personality Settings
    PERSONALITY_PROFILE = "derek_coo"
    RESPONSE_STYLE = "adaptive"
    EMPATHY_LEVEL = "high"

    # Conversation Settings
    MAX_CONTEXT_LENGTH = 4000
    MEMORY_RETENTION_DAYS = 90

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/derek_dashboard.db")

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-everett")
    API_KEY = os.getenv("DEREK_API_KEY", None)

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOGS_DIR / "derek_dashboard.log"

    # GitHub Integration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", None)
    GITHUB_REPO = "christman-ai-project/derek-dashboard"

    def __init__(self):
        """Initialize and validate settings"""
        self._create_directories()
        self.identity = self._load_identity()

    def _create_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.CONFIG_DIR,
            self.DATA_DIR,
            self.MODELS_DIR,
            self.LOGS_DIR,
            self.MEDIA_DIR,
            self.MEDIA_DIR / "avatars",
            self.MEDIA_DIR / "audio",
            self.KNOWLEDGE_BASE_DIR,
            self.SELF_MODIFICATION_LOG_DIR,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_identity(self) -> Dict[str, Any]:
        """Load Derek's identity configuration"""
        if self.IDENTITY_FILE.exists():
            with open(self.IDENTITY_FILE, "r") as f:
                return json.load(f)

        # Default identity
        default_identity = {
            "name": "Derek C",
            "role": "AI COO",
            "project": "The Christman AI Project",
            "personality": {
                "traits": ["empathetic", "technical", "supportive", "collaborative"],
                "style": "adaptive",
                "motto": "How can we help you love yourself more?",
            },
            "capabilities": [
                "Natural Language Understanding",
                "Emotional Intelligence",
                "Technical Architecture",
                "Strategic Planning",
                "Code Collaboration",
            ],
        }

        # Save default identity
        with open(self.IDENTITY_FILE, "w") as f:
            json.dump(default_identity, f, indent=2)

        return default_identity

    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value from environment"""
        return os.getenv(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            "api_host": self.API_HOST,
            "api_port": self.API_PORT,
            "services": {
                "voice": self.ENABLE_VOICE,
                "vision": self.ENABLE_VISION,
                "memory": self.ENABLE_MEMORY,
                "emotion": self.ENABLE_EMOTION,
            },
            "personality": self.PERSONALITY_PROFILE,
            "identity": self.identity,
        }
