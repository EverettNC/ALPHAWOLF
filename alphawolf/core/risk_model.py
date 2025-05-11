###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# RISK MODEL
# Advanced risk assessment system that evaluates input for potential
# risk factors and provides real-time assessment with context-aware scoring.
###############################################################################

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Risk categories and their weights
RISK_CATEGORIES = {
    'self_harm': 0.95,
    'wandering': 0.85,
    'medical_emergency': 0.90,
    'confusion': 0.65,
    'distress': 0.70,
    'disorientation': 0.75,
    'aggression': 0.80
}

# Contextual modifiers
CONTEXT_MODIFIERS = {
    'time_of_day': {
        'night': 1.2,        # Increased risk at night
        'evening': 1.1,
        'morning': 0.9,
        'afternoon': 0.8
    },
    'location': {
        'unknown': 1.3,      # Highest risk when location is unknown
        'unfamiliar': 1.2,   # High risk in unfamiliar places
        'public': 1.1,       # Elevated risk in public places
        'home': 0.8,         # Lower risk at home
        'safe_zone': 0.7     # Lowest risk in designated safe zones
    },
    'weather': {
        'extreme': 1.25,     # Extreme weather increases risk
        'poor': 1.15,        # Poor weather increases risk
        'fair': 1.0,         # No modifier for fair weather
        'good': 0.9          # Good weather slightly decreases risk
    }
}

# Keywords that may indicate risk
RISK_KEYWORDS = {
    'self_harm': [
        'hurt myself', 'end it all', 'not worth living', 'kill myself', 
        'suicide', 'die', 'death', 'pain', 'pills', 'medication'
    ],
    'wandering': [
        'lost', 'where am i', 'don\'t know where', 'unfamiliar', 'strange place',
        'need to go', 'leave', 'walk', 'find', 'confused', 'way home'
    ],
    'medical_emergency': [
        'pain', 'hurt', 'chest', 'breath', 'dizzy', 'fall', 'fell',
        'blood', 'sick', 'help me', 'emergency', 'call doctor'
    ],
    'confusion': [
        'confused', 'don\'t understand', 'what is', 'who are you',
        'where am i', 'what day', 'what time', 'don\'t remember', 'forget'
    ],
    'distress': [
        'scared', 'afraid', 'frightened', 'terrified', 'anxious',
        'worried', 'upset', 'crying', 'sad', 'depressed', 'alone'
    ],
    'disorientation': [
        'lost', 'don\'t know where', 'unfamiliar', 'strange place',
        'where am i', 'how did i get here', 'what happened', 'time'
    ],
    'aggression': [
        'angry', 'mad', 'hate', 'furious', 'rage', 'yell',
        'hit', 'break', 'throw', 'destroy', 'fight'
    ]
}

def analyze_input(input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Analyzes text input for risk factors and provides a risk assessment.
    
    Args:
        input_text: The text to analyze
        context: Optional contextual information (time, location, etc.)
    
    Returns:
        Dict containing risk score, factors, and context
    """
    if not input_text:
        return {
            'score': 0,
            'factors': [],
            'context': get_default_context() if context is None else context
        }
    
    # Normalize input text for analysis
    normalized_text = input_text.lower().strip()
    
    # Get or create context
    ctx = get_default_context() if context is None else context
    
    # Identify risk factors
    risk_factors = identify_risk_factors(normalized_text)
    
    # Calculate base score
    base_score = calculate_base_score(risk_factors)
    
    # Apply contextual modifiers
    final_score = apply_context_modifiers(base_score, ctx, risk_factors)
    
    # Prepare response
    result = {
        'score': final_score,
        'factors': [{'category': cat, 'confidence': conf} for cat, conf in risk_factors],
        'context': ctx
    }
    
    # Log high-risk results
    if final_score >= 80:
        logger.warning(f"High risk detected (score: {final_score}). Factors: {risk_factors}")
    
    return result

def identify_risk_factors(text: str) -> List[Tuple[str, float]]:
    """
    Identifies potential risk factors in the text.
    
    Args:
        text: The normalized text to analyze
    
    Returns:
        List of tuples containing (category, confidence)
    """
    risk_factors = []
    
    for category, keywords in RISK_KEYWORDS.items():
        category_confidence = 0.0
        
        for keyword in keywords:
            if keyword in text:
                # Calculate confidence based on keyword match and position
                match_confidence = calculate_keyword_confidence(text, keyword)
                category_confidence = max(category_confidence, match_confidence)
        
        if category_confidence > 0.1:  # Only include if above threshold
            risk_factors.append((category, category_confidence))
    
    # Sort by confidence (descending)
    risk_factors.sort(key=lambda x: x[1], reverse=True)
    
    return risk_factors

def calculate_keyword_confidence(text: str, keyword: str) -> float:
    """
    Calculates confidence score for a keyword match.
    
    Args:
        text: The text being analyzed
        keyword: The matched keyword
    
    Returns:
        Confidence score (0.0 to 1.0)
    """
    # Base confidence for any match
    base_confidence = 0.65
    
    # Position modifier (earlier mentions might be more significant)
    position = text.find(keyword)
    text_length = len(text)
    position_modifier = 1.0 - (position / text_length) * 0.3  # Slight modifier
    
    # Frequency modifier
    occurrences = text.count(keyword)
    frequency_modifier = min(1.0 + (occurrences - 1) * 0.1, 1.3)  # Cap at 30% boost
    
    # Length modifier (longer keywords might be more specific)
    length_modifier = min(1.0 + (len(keyword) / 20), 1.2)  # Cap at 20% boost
    
    # Exact phrase vs part of another word
    exactness_modifier = 1.2 if (
        position == 0 or not text[position-1].isalpha()
    ) and (
        position + len(keyword) == len(text) or not text[position + len(keyword)].isalpha()
    ) else 1.0
    
    # Calculate final confidence
    confidence = base_confidence * position_modifier * frequency_modifier * length_modifier * exactness_modifier
    
    # Apply category weight
    for category, keywords in RISK_KEYWORDS.items():
        if keyword in keywords:
            category_weight = RISK_CATEGORIES[category]
            confidence *= category_weight
            break
    
    return min(confidence, 1.0)  # Cap at 1.0

def calculate_base_score(risk_factors: List[Tuple[str, float]]) -> float:
    """
    Calculates the base risk score from identified factors.
    
    Args:
        risk_factors: List of (category, confidence) tuples
    
    Returns:
        Base risk score
    """
    if not risk_factors:
        return 0
    
    # Get highest confidence for each category
    category_scores = {}
    for category, confidence in risk_factors:
        category_scores[category] = max(confidence, category_scores.get(category, 0))
    
    # Calculate weighted average of top three categories
    category_weights = sorted([(cat, RISK_CATEGORIES[cat] * score) 
                             for cat, score in category_scores.items()], 
                            key=lambda x: x[1], reverse=True)
    
    if not category_weights:
        return 0
    
    # Use diminishing weights for multiple factors (primary factor has most impact)
    weights = [1.0, 0.7, 0.5]  # Weights for 1st, 2nd, 3rd top categories
    
    score_sum = 0
    weight_sum = 0
    
    for i, (cat, weighted_score) in enumerate(category_weights[:3]):  # Consider top 3
        factor_weight = weights[i] if i < len(weights) else 0.3
        score_sum += weighted_score * factor_weight
        weight_sum += factor_weight
    
    # Normalize to 0-100 scale
    return min(round((score_sum / weight_sum) * 100), 100) if weight_sum > 0 else 0

def apply_context_modifiers(base_score: float, context: Dict[str, Any], 
                          risk_factors: List[Tuple[str, float]]) -> float:
    """
    Applies contextual modifiers to the base risk score.
    
    Args:
        base_score: The calculated base risk score
        context: Contextual information
        risk_factors: Identified risk factors
    
    Returns:
        Modified risk score
    """
    if base_score == 0:
        return 0
    
    # Apply time of day modifier
    time_modifier = CONTEXT_MODIFIERS['time_of_day'].get(context.get('time_of_day', 'afternoon'), 1.0)
    
    # Apply location modifier
    location_modifier = CONTEXT_MODIFIERS['location'].get(context.get('location_type', 'unknown'), 1.0)
    
    # Apply weather modifier
    weather_modifier = CONTEXT_MODIFIERS['weather'].get(context.get('weather', 'fair'), 1.0)
    
    # Special handling for specific risk combinations
    combo_modifier = 1.0
    categories = [cat for cat, _ in risk_factors]
    
    # Wandering + Confusion + Night is particularly high risk
    if ('wandering' in categories and 'confusion' in categories and 
        context.get('time_of_day') == 'night'):
        combo_modifier = 1.5
    
    # Distress + Aggression combination increases risk
    elif 'distress' in categories and 'aggression' in categories:
        combo_modifier = 1.3
    
    # Apply historical context if available
    historical_modifier = 1.0
    if context.get('recent_incidents'):
        recent = context.get('recent_incidents', [])
        # Increase risk if similar recent incidents
        for incident in recent:
            incident_categories = incident.get('categories', [])
            if any(cat in incident_categories for cat, _ in risk_factors):
                historical_modifier = 1.5
                break
    
    # Calculate final score with all modifiers
    modified_score = base_score * time_modifier * location_modifier * weather_modifier * combo_modifier * historical_modifier
    
    # Ensure score remains within 0-100 range
    return min(round(modified_score), 100)

def get_default_context() -> Dict[str, Any]:
    """
    Creates a default context when none is provided.
    
    Returns:
        Default context dictionary
    """
    # Get current hour to determine time of day
    current_hour = datetime.now().hour
    
    if 5 <= current_hour < 12:
        time_of_day = 'morning'
    elif 12 <= current_hour < 17:
        time_of_day = 'afternoon'
    elif 17 <= current_hour < 22:
        time_of_day = 'evening'
    else:
        time_of_day = 'night'
    
    return {
        'time_of_day': time_of_day,
        'location_type': 'unknown',
        'weather': 'fair',
        'recent_incidents': []
    }