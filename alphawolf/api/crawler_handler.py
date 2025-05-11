###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# WEB CRAWLER LAMBDA HANDLER
# Serverless function for scheduled crawling of information sources.
###############################################################################

import json
import logging
import os
import sys
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.web_crawler import WebCrawler
from core.utils import log_event

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize services
web_crawler = WebCrawler()

def lambda_handler(event, context):
    """
    Lambda handler for scheduled web crawling.
    
    Args:
        event: CloudWatch Events/EventBridge or API Gateway event
        context: Lambda context
        
    Returns:
        Execution result
    """
    try:
        # Check if this is an API Gateway event or scheduled event
        is_api_request = 'httpMethod' in event or 'requestContext' in event
        
        if is_api_request:
            # Process as API Gateway request
            return handle_api_request(event)
        else:
            # Process as scheduled event
            return handle_scheduled_event(event)
            
    except Exception as e:
        # Log error
        logger.error(f"Error in crawler handler: {str(e)}")
        
        # Return error response
        return {
            'statusCode': 500 if is_api_request else 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            } if is_api_request else {},
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }) if is_api_request else {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
        }

def handle_api_request(event):
    """
    Handle API Gateway request for crawling.
    
    Args:
        event: API Gateway event
        
    Returns:
        API Gateway response
    """
    # Parse request body
    body = {}
    if 'body' in event and event['body']:
        try:
            body = json.loads(event['body'])
        except:
            logger.error("Failed to parse request body as JSON")
    
    # Extract query parameters
    query_params = event.get('queryStringParameters', {}) or {}
    
    # Get parameters, prioritizing body over query parameters
    client_id = body.get('client_id', query_params.get('client_id', 'anonymous'))
    topic = body.get('topic', query_params.get('topic'))
    force_refresh = body.get('force_refresh', query_params.get('force_refresh', 'false')).lower() == 'true'
    
    # Get source status if requested
    if body.get('action', '') == 'status' or query_params.get('action', '') == 'status':
        status = web_crawler.get_source_status()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'client_id': client_id,
                'source_status': status,
                'timestamp': datetime.utcnow().isoformat() + "Z"
            })
        }
    
    # Perform crawl
    logger.info(f"Starting crawl for client {client_id}, topic: {topic or 'all'}, force_refresh: {force_refresh}")
    start_time = time.time()
    
    crawl_result = web_crawler.crawl(topic, force_refresh)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log the event
    log_event(client_id, {
        'event_type': 'web_crawl',
        'topic': topic,
        'force_refresh': force_refresh,
        'sources_processed': crawl_result.get('sources_processed', 0),
        'new_content': crawl_result.get('new_content', 0),
        'updated_content': crawl_result.get('updated_content', 0),
        'errors': crawl_result.get('errors', 0),
        'duration_seconds': duration,
        'timestamp': datetime.utcnow().isoformat() + "Z"
    })
    
    # Return response
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'client_id': client_id,
            'crawl_result': {
                'topic': topic,
                'sources_processed': crawl_result.get('sources_processed', 0),
                'new_content': crawl_result.get('new_content', 0),
                'updated_content': crawl_result.get('updated_content', 0),
                'errors': crawl_result.get('errors', 0),
                'topics': crawl_result.get('topics', []),
                'duration_seconds': duration,
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
        })
    }

def handle_scheduled_event(event):
    """
    Handle scheduled event for crawling.
    
    Args:
        event: CloudWatch Events/EventBridge event
        
    Returns:
        Execution result
    """
    # Check if specific topics are requested in the event
    topics = event.get('topics', [])
    
    # Load configuration from environment variable
    sources_config = os.environ.get('SOURCES_CONFIG')
    if sources_config:
        try:
            config = json.loads(sources_config)
            if 'topics' in config:
                topics.extend(config.get('topics', []))
        except:
            logger.error("Failed to parse SOURCES_CONFIG environment variable")
    
    # If no topics specified, crawl all sources
    if not topics:
        logger.info("Starting crawl for all topics (scheduled event)")
        crawl_result = web_crawler.crawl(force_refresh=False)
        
        return {
            'success': True,
            'sources_processed': crawl_result.get('sources_processed', 0),
            'new_content': crawl_result.get('new_content', 0),
            'updated_content': crawl_result.get('updated_content', 0),
            'errors': crawl_result.get('errors', 0),
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
    
    # Crawl each topic
    results = []
    for topic in topics:
        logger.info(f"Starting crawl for topic: {topic} (scheduled event)")
        crawl_result = web_crawler.crawl(topic, force_refresh=False)
        
        results.append({
            'topic': topic,
            'sources_processed': crawl_result.get('sources_processed', 0),
            'new_content': crawl_result.get('new_content', 0),
            'updated_content': crawl_result.get('updated_content', 0),
            'errors': crawl_result.get('errors', 0)
        })
    
    return {
        'success': True,
        'topic_results': results,
        'timestamp': datetime.utcnow().isoformat() + "Z"
    }