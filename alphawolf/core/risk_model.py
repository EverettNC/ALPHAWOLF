###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# RISK MODEL
# Analyzes input text for patterns indicating potential risk factors
# for dementia and Alzheimer's patients, providing risk scoring and
# contextual analysis.
###############################################################################

import re
import json
import os
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logger = logging.getLogger("alphawolf.risk")

# Risk factor categories with associated keywords
RISK_FACTORS = {
    "suicidal_ideation": {
        "keywords": [
            "kill myself", "end my life", "suicide", "want to die", "disappear", 
            "not worth living", "better off without me", "no reason to live"
        ],
        "weight": 10.0,
        "threshold": 0.5
    },
    "severe_distress": {
        "keywords": [
            "can't take it", "overwhelmed", "hopeless", "desperate", "exhausted",
            "unbearable", "suffering", "torment", "agony", "terrible pain" 
        ],
        "weight": 8.0,
        "threshold": 0.6
    },
    "disorientation": {
        "keywords": [
            "lost", "don't know where", "confused", "where am i", "strange place",
            "unfamiliar", "not home", "don't recognize", "strange people"
        ],
        "weight": 7.0,
        "threshold": 0.7
    },
    "aggression": {
        "keywords": [
            "angry", "hit", "hurt", "attack", "violent", "break", "smash",
            "hate", "furious", "rage", "fight"
        ],
        "weight": 6.5,
        "threshold": 0.6
    },
    "paranoia": {
        "keywords": [
            "watching me", "following me", "listening", "spying", "conspiracy",
            "after me", "trying to hurt me", "poisoning", "stealing", "plotting"
        ],
        "weight": 6.0,
        "threshold": 0.6
    },
    "memory_distress": {
        "keywords": [
            "forgetting", "can't remember", "memory failing", "losing my mind",
            "don't know who", "forgotten", "blank", "erased"
        ],
        "weight": 5.0,
        "threshold": 0.7
    },
    "abandonment": {
        "keywords": [
            "alone", "abandoned", "left me", "nobody cares", "forgotten me",
            "neglected", "ignored", "don't visit", "never see"
        ],
        "weight": 5.0,
        "threshold": 0.7
    }
}

def analyze_input(text: str) -> Dict[str, Any]:
    """
    Analyze input text for risk factors
    
    Args:
        text: User input text to analyze
        
    Returns:
        Dictionary with risk score and identified factors
    """
    if not text:
        return {"score": 0, "factors": []}
    
    text = text.lower()
    matched_factors = []
    total_score = 0
    
    # Check each risk factor category
    for factor, data in RISK_FACTORS.items():
        factor_matches = []
        
        # Look for keyword matches
        for keyword in data["keywords"]:
            if keyword in text:
                factor_matches.append(keyword)
        
        # Calculate factor score if matches found
        if factor_matches:
            factor_score = min(1.0, len(factor_matches) / len(data["keywords"]))
            if factor_score >= data["threshold"]:
                factor_weight = data["weight"]
                weighted_score = factor_score * factor_weight
                total_score += weighted_score
                
                matched_factors.append({
                    "factor": factor,
                    "keywords": factor_matches,
                    "score": factor_score * 100,
                    "weight": factor_weight,
                    "weighted_score": weighted_score
                })
    
    # Scale total score to 0-100 range
    max_possible_score = sum(factor["weight"] for factor in RISK_FACTORS.values())
    normalized_score = min(100, int((total_score / max_possible_score) * 100))
    
    # Add context analysis
    context = analyze_context(text, matched_factors)
    
    return {
        "score": normalized_score,
        "factors": matched_factors,
        "context": context
    }

def analyze_context(text: str, matched_factors: List[Dict]) -> Optional[Dict]:
    """
    Perform deeper context analysis on the input text
    
    Args:
        text: User input text
        matched_factors: List of factors already identified
        
    Returns:
        Dictionary with contextual analysis results
    """
    # Skip detailed analysis if no risk factors identified
    if not matched_factors:
        return None
    
    context = {}
    
    # Check for temporal indicators
    temporal_markers = ["now", "right now", "tonight", "today", "soon", "immediately"]
    for marker in temporal_markers:
        if marker in text.lower():
            context["temporal_urgency"] = True
            context["temporal_marker"] = marker
            break
    
    # Check for definiteness indicators
    definite_markers = ["will", "going to", "decided to", "planned", "definitely"]
    for marker in definite_markers:
        if marker in text.lower():
            context["definiteness"] = True
            context["definite_marker"] = marker
            break
    
    # Check for isolation indicators
    isolation_markers = ["alone", "nobody", "no one", "by myself", "isolated"]
    for marker in isolation_markers:
        if marker in text.lower():
            context["isolation"] = True
            context["isolation_marker"] = marker
            break
    
    # Check for length-based intensity
    if len(text.split()) > 15:
        context["detailed_expression"] = True
    
    return context