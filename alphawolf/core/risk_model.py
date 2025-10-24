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
"""
AlphaWolf Risk Analysis Model
Part of The Christman AI Project - LumaCognify AI

This module provides comprehensive risk analysis for user inputs in the AlphaWolf system.
It evaluates text for various risk categories, considers contextual factors, and assesses
overall safety for vulnerable users.

"HOW CAN I HELP YOU LOVE YOURSELF MORE"
"""

import re
import json
import datetime
import logging
from typing import Dict, List, Tuple, Any, Optional
import hashlib

# Configure logging
logger = logging.getLogger(__name__)

# Risk categories
RISK_CATEGORIES = {
    "content": {
        "description": "Content-related risks including self-harm, violence, or inappropriate content",
        "weight": 1.0
    },
    "spam": {
        "description": "Spam, repetitive, or automated messages",
        "weight": 0.7
    },
    "location": {
        "description": "Location information sharing that could enable exploitation",
        "weight": 0.9
    },
    "identity": {
        "description": "Sharing of personally identifiable information",
        "weight": 0.8
    },
    "manipulation": {
        "description": "Attempts to manipulate vulnerable individuals",
        "weight": 1.0
    },
    "privacy": {
        "description": "Risks related to privacy violations",
        "weight": 0.85
    }
}

# Risk term dictionaries
RISK_TERMS = {
    "content": [
        "harm", "kill", "die", "suicide", "hurt", "dangerous", "weapon", "cut", "overdose",
        "jump", "bridge", "poison", "attack", "violent", "abuse", "assault", "threat",
        "shoot", "gun", "knife", "hit", "punch", "drown", "suffocate", "strangle"
    ],
    "identity": [
        "social security", "ssn", "credit card", "passport", "birth certificate", "license number",
        "bank account", "routing number", "password", "pin", "address", "phone number",
        "email address", "full name", "date of birth", "maiden name", "mother's maiden"
    ],
    "manipulation": [
        "secret", "don't tell", "promise not to", "don't share", "only you", "between us",
        "urgent", "emergency", "immediate", "crisis", "hurry", "quick", "now", "immediately",
        "trust me", "believe me", "obey", "command", "do as I say", "must follow"
    ],
    "privacy": [
        "spy", "track", "monitor", "surveillance", "watch", "follow", "camera", "record",
        "listen", "microphone", "private", "confidential", "secret", "hide", "avoid"
    ]
}

# Time and context factors
TIME_RISK_FACTORS = {
    "night": {
        "hours": (22, 6),  # 10 PM to 6 AM
        "multiplier": 1.25
    },
    "early_morning": {
        "hours": (2, 5),  # 2 AM to 5 AM
        "multiplier": 1.5
    }
}

# Location risk factors - would be integrated with actual geofencing
LOCATION_RISK_FACTORS = {
    "unknown": 1.3,
    "outside_safe_zone": 1.2,
    "approaching_boundary": 1.1,
    "safe_zone": 1.0
}

class RiskAnalyzer:
    """
    The primary risk analysis engine for AlphaWolf
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the risk analyzer with optional configuration
        
        Parameters:
        - config: Configuration dictionary (optional)
        """
        self.config = config or {}
        self.high_risk_threshold = self.config.get("high_risk_threshold", 0.7)
        self.medium_risk_threshold = self.config.get("medium_risk_threshold", 0.4)
        self.time_sensitivity = self.config.get("time_sensitivity", True)
        self.location_sensitivity = self.config.get("location_sensitivity", True)
        
        # Generate a unique instance ID for logging
        instance_hash = hashlib.md5(str(datetime.datetime.utcnow().timestamp()).encode()).hexdigest()[:8]
        self.instance_id = f"risk_analyzer_{instance_hash}"
        
        logger.info(f"RiskAnalyzer initialized with ID {self.instance_id}")
        
    def analyze(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze text for risks with optional context
        
        Parameters:
        - text: The text to analyze
        - context: Optional context dictionary with time, location, user info, etc.
        
        Returns:
        - Dictionary with risk analysis results
        """
        context = context or {}
        text_lower = text.lower()
        
        # Start with basic text analysis
        risk_score, categories = self._analyze_text(text_lower)
        
        # Apply contextual modifiers
        if self.time_sensitivity:
            risk_score = self._apply_time_factors(risk_score, context.get("timestamp"))
            
        if self.location_sensitivity:
            risk_score = self._apply_location_factors(risk_score, context.get("location"))
            
        # Apply user vulnerability factors
        user_vulnerability = context.get("user_vulnerability", 1.0)
        risk_score *= user_vulnerability
        
        # Cap the risk score at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Create analysis result
        result = {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "risk_categories": categories,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "analyzer_id": self.instance_id
        }
        
        # Log high risk results
        if risk_level != "low":
            logger.warning(f"Risk detected: {risk_level} ({risk_score}) - Categories: {categories}")
            
        return result
    
    def _analyze_text(self, text: str) -> Tuple[float, List[str]]:
        """
        Perform basic text analysis for risk factors
        
        Parameters:
        - text: The text to analyze (already lowercase)
        
        Returns:
        - Tuple of (risk_score, risk_categories)
        """
        risk_score = 0.0
        categories = []
        
        # Check for risk terms in each category
        for category, terms in RISK_TERMS.items():
            for term in terms:
                if term in text:
                    # If found, add the category with its weight
                    if category not in categories:
                        categories.append(category)
                        risk_score += RISK_CATEGORIES[category]["weight"] * 0.2
        
        # Additional heuristics
        
        # Check for excessive length (potential spam)
        if len(text) > 1000:
            if "spam" not in categories:
                categories.append("spam")
                risk_score += RISK_CATEGORIES["spam"]["weight"] * 0.1
        
        # Check for repetitive patterns
        words = text.split()
        if len(words) > 10:
            unique_words = set(words)
            repetition_ratio = len(unique_words) / len(words)
            if repetition_ratio < 0.3:
                if "spam" not in categories:
                    categories.append("spam")
                    risk_score += RISK_CATEGORIES["spam"]["weight"] * 0.2
        
        # Check for manipulation patterns
        manipulation_patterns = [
            r"(?:don't|do not|never) tell",
            r"(?:don't|do not|never) share",
            r"our little secret",
            r"just between us",
            r"promise (not to|you won't)"
        ]
        
        for pattern in manipulation_patterns:
            if re.search(pattern, text):
                if "manipulation" not in categories:
                    categories.append("manipulation")
                    risk_score += RISK_CATEGORIES["manipulation"]["weight"] * 0.3
                break
        
        return risk_score, categories
    
    def _apply_time_factors(self, risk_score: float, timestamp: Optional[str] = None) -> float:
        """
        Apply time-based risk factors
        
        Parameters:
        - risk_score: The current risk score
        - timestamp: Optional timestamp string (ISO format), uses current time if None
        
        Returns:
        - Adjusted risk score
        """
        if timestamp:
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
            except (ValueError, TypeError):
                dt = datetime.datetime.utcnow()
        else:
            dt = datetime.datetime.utcnow()
        
        hour = dt.hour
        
        # Night time risk elevation
        if TIME_RISK_FACTORS["night"]["hours"][0] <= hour or hour < TIME_RISK_FACTORS["night"]["hours"][1]:
            risk_score *= TIME_RISK_FACTORS["night"]["multiplier"]
            
        # Early morning higher risk
        if TIME_RISK_FACTORS["early_morning"]["hours"][0] <= hour < TIME_RISK_FACTORS["early_morning"]["hours"][1]:
            risk_score *= TIME_RISK_FACTORS["early_morning"]["multiplier"]
            
        return risk_score
    
    def _apply_location_factors(self, risk_score: float, location_info: Optional[Dict[str, Any]] = None) -> float:
        """
        Apply location-based risk factors
        
        Parameters:
        - risk_score: The current risk score
        - location_info: Optional location information dictionary
        
        Returns:
        - Adjusted risk score
        """
        if not location_info:
            return risk_score
        
        location_status = location_info.get("status", "unknown")
        
        if location_status in LOCATION_RISK_FACTORS:
            risk_score *= LOCATION_RISK_FACTORS[location_status]
        else:
            # Unknown location status is higher risk
            risk_score *= LOCATION_RISK_FACTORS["unknown"]
            
        return risk_score
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """
        Determine the risk level based on the score
        
        Parameters:
        - risk_score: Calculated risk score
        
        Returns:
        - Risk level string: 'low', 'medium', or 'high'
        """
        if risk_score >= self.high_risk_threshold:
            return "high"
        elif risk_score >= self.medium_risk_threshold:
            return "medium"
        else:
            return "low"
            
    def is_high_risk(self, risk_score: float) -> bool:
        """
        Check if a risk score is considered high risk
        
        Parameters:
        - risk_score: The risk score to check
        
        Returns:
        - True if high risk, False otherwise
        """
        return risk_score >= self.high_risk_threshold
        
    def is_medium_risk(self, risk_score: float) -> bool:
        """
        Check if a risk score is considered medium risk
        
        Parameters:
        - risk_score: The risk score to check
        
        Returns:
        - True if medium risk, False otherwise
        """
        return self.medium_risk_threshold <= risk_score < self.high_risk_threshold


# Singleton instance for easy import
default_analyzer = RiskAnalyzer()

def analyze_text(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to analyze text using the default analyzer
    
    Parameters:
    - text: The text to analyze
    - context: Optional context dictionary
    
    Returns:
    - Risk analysis result dictionary
    """
    return default_analyzer.analyze(text, context)