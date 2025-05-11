###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# LAMBDA FUNCTION HANDLER
# Serverless entry point for processing events, analyzing risk, 
# and triggering appropriate responses based on context evaluation.
###############################################################################

import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import risk_model
from core import utils
from core.family_protection import FamilyProtectionSystem
from core.web_crawler import WebCrawler

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize services
family_protection = FamilyProtectionSystem()
web_crawler = WebCrawler()

def lambda_handler(event, context):
    """
    Main Lambda handler function for API Gateway events.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract HTTP method and path
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        path = event.get('path', event.get('requestContext', {}).get('http', {}).get('path', ''))
        
        # Parse request body if present
        body = {}
        if 'body' in event and event['body']:
            try:
                body = json.loads(event['body'])
            except:
                logger.error("Failed to parse request body as JSON")
                body = {}
        
        # Route request based on path and method
        if path == '/intents' and method == 'POST':
            response = process_intent(body)
        elif path == '/analyze' and method == 'POST':
            response = process_risk_analysis(body)
        elif path == '/safezones' and method == 'POST':
            response = process_safe_zone_request(body)
        elif path == '/content' and method == 'GET':
            response = process_content_request(event.get('queryStringParameters', {}))
        else:
            response = {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Not found',
                    'message': f"No handler for {method} {path}"
                })
            }
        
        # Add CORS headers to all responses
        if 'headers' not in response:
            response['headers'] = {}
        
        response['headers'].update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        
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

def process_intent(body: Dict[str, Any]):
    """
    Process intent request from client.
    
    Args:
        body: Request body
        
    Returns:
        API Gateway response
    """
    client_id = body.get('client_id', 'anonymous')
    intent = body.get('intent', '')
    input_text = body.get('input', '')
    session_id = body.get('session_id', utils.generate_session_id())
    
    logger.info(f"Processing intent '{intent}' for client {client_id}")
    
    # Get client configuration
    client_config = utils.get_client_config(client_id)
    
    # Handle different intents
    if intent == 'analyze_risk':
        # Analyze input for risk
        analysis_result = risk_model.analyze_input(input_text)
        
        # Check if high risk and family protection is enabled
        risk_score = analysis_result.get('score', 0)
        is_high_risk = risk_score >= client_config.get('preferences', {}).get('alert_threshold', 70)
        
        response_data = {
            'client_id': client_id,
            'session_id': session_id,
            'intent': intent,
            'risk_assessment': {
                'score': risk_score,
                'is_high_risk': is_high_risk,
                'factors': analysis_result.get('factors', [])
            },
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
        
        # Add family protection assessment if enabled and high risk
        if is_high_risk and client_config.get('features', {}).get('family_protection', False):
            aegis_assessment = family_protection.integrate_with_aegis(
                client_id,
                {
                    'risk_score': risk_score,
                    'risk_factors': analysis_result.get('factors', [])
                }
            )
            response_data['aegis_assessment'] = aegis_assessment.get('aegis_assessment', {})
        
        # Log the event
        utils.log_event(client_id, {
            'event_type': 'intent_processed',
            'intent': intent,
            'session_id': session_id,
            'risk_score': risk_score,
            'is_high_risk': is_high_risk
        })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response_data)
        }
        
    elif intent == 'update_location':
        # Extract location data
        location = body.get('location', {})
        latitude = location.get('latitude')
        longitude = location.get('longitude')
        
        if latitude is None or longitude is None:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'Missing location data',
                    'message': 'Latitude and longitude are required',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                })
            }
        
        # Check location safety if feature is enabled
        if client_config.get('features', {}).get('location_tracking', False):
            safety_result = family_protection.check_location_safety(
                client_id,
                float(latitude),
                float(longitude)
            )
            
            response_data = {
                'client_id': client_id,
                'session_id': session_id,
                'intent': intent,
                'location_safety': safety_result,
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
            
            # Log the event
            utils.log_event(client_id, {
                'event_type': 'location_updated',
                'session_id': session_id,
                'latitude': latitude,
                'longitude': longitude,
                'is_safe': safety_result.get('is_safe')
            })
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(response_data)
            }
        else:
            # Location tracking not enabled
            return {
                'statusCode': 403,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'Feature not enabled',
                    'message': 'Location tracking is not enabled for this client',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                })
            }
            
    elif intent == 'get_content':
        # Get content for topic if feature is enabled
        topic = body.get('topic', 'alzheimer\'s')
        
        if client_config.get('features', {}).get('web_content', False):
            content = web_crawler.get_content_for_topic(topic)
            
            response_data = {
                'client_id': client_id,
                'session_id': session_id,
                'intent': intent,
                'topic': topic,
                'content': content,
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
            
            # Log the event
            utils.log_event(client_id, {
                'event_type': 'content_requested',
                'session_id': session_id,
                'topic': topic,
                'content_count': len(content)
            })
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(response_data)
            }
        else:
            # Web content not enabled
            return {
                'statusCode': 403,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'Feature not enabled',
                    'message': 'Web content is not enabled for this client',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                })
            }
    
    # Unknown intent
    return {
        'statusCode': 400,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'error': 'Unknown intent',
            'message': f"Intent '{intent}' is not supported",
            'timestamp': datetime.utcnow().isoformat() + "Z"
        })
    }

def process_risk_analysis(body: Dict[str, Any]):
    """
    Process risk analysis request.
    
    Args:
        body: Request body
        
    Returns:
        API Gateway response
    """
    client_id = body.get('client_id', 'anonymous')
    input_text = body.get('input', '')
    session_id = body.get('session_id', utils.generate_session_id())
    context = body.get('context', {})
    
    # Sanitize input
    sanitized_input = utils.sanitize_input(input_text)
    
    # Analyze risk
    analysis_result = risk_model.analyze_input(sanitized_input, context)
    
    # Prepare response
    response_data = {
        'client_id': client_id,
        'session_id': session_id,
        'risk_assessment': analysis_result,
        'timestamp': datetime.utcnow().isoformat() + "Z"
    }
    
    # Log the event
    utils.log_event(client_id, {
        'event_type': 'risk_analyzed',
        'session_id': session_id,
        'risk_score': analysis_result.get('score', 0),
        'risk_factors_count': len(analysis_result.get('factors', []))
    })
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response_data)
    }

def process_safe_zone_request(body: Dict[str, Any]):
    """
    Process safe zone request.
    
    Args:
        body: Request body
        
    Returns:
        API Gateway response
    """
    client_id = body.get('client_id', 'anonymous')
    action = body.get('action', '')
    zone_data = body.get('zone', {})
    
    if action == 'add':
        # Add new safe zone
        result = family_protection.add_safe_zone(client_id, zone_data)
        
        return {
            'statusCode': 200 if result.get('success', False) else 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result)
        }
        
    elif action == 'get':
        # Get all safe zones
        zones = family_protection.get_client_safe_zones(client_id)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'client_id': client_id,
                'zones': zones,
                'timestamp': datetime.utcnow().isoformat() + "Z"
            })
        }
    
    # Unknown action
    return {
        'statusCode': 400,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'error': 'Unknown action',
            'message': f"Action '{action}' is not supported for safe zones",
            'timestamp': datetime.utcnow().isoformat() + "Z"
        })
    }

def process_content_request(params: Dict[str, str]):
    """
    Process content request.
    
    Args:
        params: Query string parameters
        
    Returns:
        API Gateway response
    """
    client_id = params.get('client_id', 'anonymous')
    topic = params.get('topic', 'alzheimer\'s')
    force_refresh = params.get('refresh', 'false').lower() == 'true'
    
    # Get client configuration
    client_config = utils.get_client_config(client_id)
    
    if client_config.get('features', {}).get('web_content', False):
        # If force refresh, crawl new content
        if force_refresh:
            crawl_result = web_crawler.crawl(topic, force_refresh=True)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'client_id': client_id,
                    'topic': topic,
                    'crawl_result': crawl_result,
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                })
            }
        else:
            # Get cached content
            max_age_days = int(params.get('max_age', '30'))
            content = web_crawler.get_content_for_topic(topic, max_age_days=max_age_days)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'client_id': client_id,
                    'topic': topic,
                    'content': content,
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                })
            }
    else:
        # Web content not enabled
        return {
            'statusCode': 403,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Feature not enabled',
                'message': 'Web content is not enabled for this client',
                'timestamp': datetime.utcnow().isoformat() + "Z"
            })
        }