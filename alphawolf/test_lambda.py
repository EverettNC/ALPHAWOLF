###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# LAMBDA FUNCTION TESTER
# Utility script to test Lambda handlers locally
###############################################################################

import json
import logging
import os
import sys
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Lambda handlers
try:
    from api.lambda_function import lambda_handler as main_handler
    from api.risk_analyzer import lambda_handler as risk_handler
    from api.safety_check import lambda_handler as safety_handler
    from api.crawler_handler import lambda_handler as crawler_handler
    from api.alert_processor import lambda_handler as alert_handler
    
    logger.info("Successfully imported all Lambda handlers")
except Exception as e:
    logger.error(f"Error importing Lambda handlers: {str(e)}")
    sys.exit(1)

def test_all_handlers():
    """Run tests for all Lambda handlers."""
    logger.info("Starting Lambda handler tests")
    
    # Test main Lambda handler
    test_main_handler()
    
    # Test risk analyzer
    test_risk_analyzer()
    
    # Test safety check
    test_safety_check()
    
    # Test crawler handler
    test_crawler_handler()
    
    # Test alert processor
    test_alert_processor()
    
    logger.info("All Lambda handler tests completed")

def test_main_handler():
    """Test the main Lambda handler."""
    logger.info("Testing main Lambda handler")
    
    # Test process_intent - analyze_risk
    event = {
        'httpMethod': 'POST',
        'path': '/intents',
        'body': json.dumps({
            'client_id': 'test_client',
            'intent': 'analyze_risk',
            'input': 'I\'m feeling confused and don\'t know where I am'
        })
    }
    
    response = main_handler(event, {})
    logger.info(f"Main handler (analyze_risk) response status: {response.get('statusCode')}")
    
    # Test process_intent - update_location
    event = {
        'httpMethod': 'POST',
        'path': '/intents',
        'body': json.dumps({
            'client_id': 'test_client',
            'intent': 'update_location',
            'location': {
                'latitude': 37.7749,
                'longitude': -122.4194
            }
        })
    }
    
    response = main_handler(event, {})
    logger.info(f"Main handler (update_location) response status: {response.get('statusCode')}")
    
    # Test not found
    event = {
        'httpMethod': 'GET',
        'path': '/nonexistent'
    }
    
    response = main_handler(event, {})
    logger.info(f"Main handler (not found) response status: {response.get('statusCode')}")

def test_risk_analyzer():
    """Test the risk analyzer Lambda handler."""
    logger.info("Testing risk analyzer Lambda handler")
    
    # Test with confusion input
    event = {
        'body': json.dumps({
            'client_id': 'test_client',
            'input': 'I\'m feeling confused and don\'t know where I am',
            'session_id': 'test_session',
            'location': {
                'latitude': 37.7749,
                'longitude': -122.4194
            }
        })
    }
    
    response = risk_handler(event, {})
    logger.info(f"Risk analyzer response status: {response.get('statusCode')}")
    
    # Test with empty input
    event = {
        'body': json.dumps({
            'client_id': 'test_client',
            'input': '',
            'session_id': 'test_session'
        })
    }
    
    response = risk_handler(event, {})
    logger.info(f"Risk analyzer (empty input) response status: {response.get('statusCode')}")

def test_safety_check():
    """Test the safety check Lambda handler."""
    logger.info("Testing safety check Lambda handler")
    
    # Test with valid location
    event = {
        'body': json.dumps({
            'client_id': 'test_client',
            'location': {
                'latitude': 37.7749,
                'longitude': -122.4194
            },
            'session_id': 'test_session'
        })
    }
    
    response = safety_handler(event, {})
    logger.info(f"Safety check response status: {response.get('statusCode')}")
    
    # Test with missing location
    event = {
        'body': json.dumps({
            'client_id': 'test_client',
            'session_id': 'test_session'
        })
    }
    
    response = safety_handler(event, {})
    logger.info(f"Safety check (missing location) response status: {response.get('statusCode')}")

def test_crawler_handler():
    """Test the crawler handler Lambda handler."""
    logger.info("Testing crawler handler Lambda handler")
    
    # Test API request
    event = {
        'httpMethod': 'GET',
        'queryStringParameters': {
            'client_id': 'test_client',
            'topic': 'alzheimer\'s'
        }
    }
    
    response = crawler_handler(event, {})
    logger.info(f"Crawler handler (API) response status: {response.get('statusCode')}")
    
    # Test scheduled event
    event = {
        'source': 'aws.events',
        'topics': ['alzheimer\'s', 'dementia']
    }
    
    response = crawler_handler(event, {})
    logger.info(f"Crawler handler (scheduled) success: {response.get('success')}")

def test_alert_processor():
    """Test the alert processor Lambda handler."""
    logger.info("Testing alert processor Lambda handler")
    
    # Test with valid records
    event = {
        'Records': [
            {
                'messageId': 'test_message_1',
                'body': json.dumps({
                    'client_id': 'test_client',
                    'alert_type': 'location_safety',
                    'severity': 'medium',
                    'message': 'Client is outside of designated safe zones'
                })
            },
            {
                'messageId': 'test_message_2',
                'body': json.dumps({
                    'client_id': 'test_client',
                    'alert_type': 'risk_assessment',
                    'severity': 'high',
                    'message': 'High risk detected: confusion and disorientation'
                })
            }
        ]
    }
    
    response = alert_handler(event, {})
    logger.info(f"Alert processor success: {response.get('success')}")
    logger.info(f"Alert processor processed: {response.get('processed')}, successful: {response.get('successful')}")
    
    # Test with no records
    event = {}
    
    response = alert_handler(event, {})
    logger.info(f"Alert processor (no records) success: {response.get('success')}")

if __name__ == "__main__":
    # Check if specific test is requested
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "main":
            test_main_handler()
        elif test_name == "risk":
            test_risk_analyzer()
        elif test_name == "safety":
            test_safety_check()
        elif test_name == "crawler":
            test_crawler_handler()
        elif test_name == "alert":
            test_alert_processor()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: main, risk, safety, crawler, alert")
    else:
        # Run all tests
        test_all_handlers()