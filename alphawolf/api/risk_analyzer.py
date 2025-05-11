###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# RISK ANALYZER LAMBDA HANDLER
# Serverless function for analyzing input text and detecting potential
# risks, with context-aware escalation for family protection.
###############################################################################

import json
import os
import sys
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.risk_model import analyze_input
from core.family_protection import FamilyProtectionSystem
from core.utils import log_event, generate_session_id, sanitize_input

# Initialize services
family_protection = FamilyProtectionSystem()

def lambda_handler(event, context):
    """
    Lambda handler for risk analysis API endpoint
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Extract parameters
        user_input = sanitize_input(body.get('input', ''))
        client_id = body.get('client_id', 'anonymous')
        session_id = body.get('session_id', generate_session_id())
        location = body.get('location', {})
        
        # Get current timestamp
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Analyze input for risk factors
        start_time = time.time()
        risk_analysis = analyze_input(user_input)
        analysis_time = int((time.time() - start_time) * 1000)  # ms
        
        # Determine risk level
        risk_score = risk_analysis['score']
        risk_threshold = int(os.environ.get('RISK_THRESHOLD', '85'))
        is_high_risk = risk_score >= risk_threshold
        
        # Check location safety if coordinates provided
        location_safety = None
        if location and 'latitude' in location and 'longitude' in location:
            location_safety = family_protection.check_location_safety(
                client_id, 
                float(location['latitude']), 
                float(location['longitude'])
            )
        
        # Enhanced risk assessment with Aegis AI if applicable
        enhanced_assessment = None
        if is_high_risk or (location_safety and not location_safety['is_safe']):
            enhanced_assessment = family_protection.integrate_with_aegis(
                client_id,
                {
                    'risk_score': risk_score,
                    'risk_factors': risk_analysis.get('factors', []),
                    'location_safety': location_safety
                }
            )
        
        # Prepare response
        response = {
            'client_id': client_id,
            'session_id': session_id,
            'input_hash': hash(user_input),  # For privacy, don't return the actual input
            'risk_score': risk_score,
            'is_high_risk': is_high_risk,
            'risk_factors': risk_analysis.get('factors', []),
            'context': risk_analysis.get('context'),
            'location_safety': location_safety,
            'enhanced_assessment': enhanced_assessment,
            'timestamp': timestamp,
            'analysis_time_ms': analysis_time
        }
        
        # Log the event
        log_event(client_id, {
            'event_type': 'risk_analysis',
            'session_id': session_id,
            'risk_score': risk_score,
            'is_high_risk': is_high_risk,
            'location_safe': location_safety['is_safe'] if location_safety else None,
            'timestamp': timestamp
        })
        
        # Return API response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response)
        }
        
    except Exception as e:
        # Log error
        error_message = f"Error in risk analyzer: {str(e)}"
        print(error_message)
        
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': error_message,
                'timestamp': datetime.utcnow().isoformat() + "Z"
            })
        }