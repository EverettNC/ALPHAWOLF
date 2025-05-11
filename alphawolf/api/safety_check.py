###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# SAFETY CHECK LAMBDA HANDLER
# Serverless function for checking location safety against defined safe zones.
###############################################################################

import json
import logging
import os
import sys
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.family_protection import FamilyProtectionSystem
from core.utils import log_event, generate_session_id

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize services
family_protection = FamilyProtectionSystem()

def lambda_handler(event, context):
    """
    Lambda handler for safety check API endpoint.
    
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
        client_id = body.get('client_id', 'anonymous')
        location = body.get('location', {})
        session_id = body.get('session_id', generate_session_id())
        
        # Validate required parameters
        if not location or 'latitude' not in location or 'longitude' not in location:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing location data',
                    'message': 'Both latitude and longitude are required',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                })
            }
        
        # Extract coordinates
        latitude = float(location['latitude'])
        longitude = float(location['longitude'])
        
        # Get safety radius from environment or request
        safety_radius = body.get('safety_radius', os.environ.get('SAFETY_RADIUS', 100))
        
        # Check location safety
        safety_result = family_protection.check_location_safety(
            client_id, 
            latitude, 
            longitude
        )
        
        # Add metadata to result
        result = {
            'client_id': client_id,
            'session_id': session_id,
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'safety_check': safety_result,
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
        
        # Log the event
        log_event(client_id, {
            'event_type': 'safety_check',
            'session_id': session_id,
            'latitude': latitude,
            'longitude': longitude,
            'is_safe': safety_result.get('is_safe'),
            'timestamp': datetime.utcnow().isoformat() + "Z"
        })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        # Log error
        logger.error(f"Error in safety check: {str(e)}")
        
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat() + "Z"
            })
        }