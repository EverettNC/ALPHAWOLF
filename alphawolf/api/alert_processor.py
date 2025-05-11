###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# ALERT PROCESSOR LAMBDA HANDLER
# Serverless function for processing alerts from the SQS queue.
###############################################################################

import json
import logging
import os
import sys
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import log_event, get_client_config

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda handler for processing alerts from SQS queue.
    
    Args:
        event: SQS event
        context: Lambda context
        
    Returns:
        Processing result
    """
    try:
        # Check if we have records to process
        if 'Records' not in event:
            logger.warning("No SQS records found in event")
            return {
                'success': False,
                'error': 'No SQS records found in event',
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
        
        records = event['Records']
        logger.info(f"Processing {len(records)} SQS messages")
        
        results = []
        
        # Process each record
        for record in records:
            try:
                # Parse message body
                message_body = json.loads(record['body'])
                
                # Process the alert
                result = process_alert(message_body)
                
                results.append({
                    'message_id': record.get('messageId', 'unknown'),
                    'success': result.get('success', False),
                    'error': result.get('error') if not result.get('success', False) else None
                })
                
            except Exception as e:
                logger.error(f"Error processing SQS message: {str(e)}")
                results.append({
                    'message_id': record.get('messageId', 'unknown'),
                    'success': False,
                    'error': str(e)
                })
        
        # Summarize results
        successful = sum(1 for r in results if r.get('success', False))
        
        return {
            'success': True,
            'processed': len(records),
            'successful': successful,
            'failed': len(records) - successful,
            'results': results,
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        # Log error
        logger.error(f"Error in alert processor: {str(e)}")
        
        # Return error response
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }

def process_alert(alert):
    """
    Process an individual alert.
    
    Args:
        alert: Alert data from SQS
        
    Returns:
        Processing result
    """
    start_time = time.time()
    
    try:
        # Extract alert information
        client_id = alert.get('client_id', 'anonymous')
        alert_type = alert.get('alert_type', 'unknown')
        severity = alert.get('severity', 'medium')
        message = alert.get('message', 'No message provided')
        
        logger.info(f"Processing {severity} {alert_type} alert for client {client_id}")
        
        # Get client configuration
        client_config = get_client_config(client_id)
        
        # Determine notification channels based on severity and client preferences
        channels = determine_notification_channels(client_config, severity)
        
        # Send notifications through each channel
        notification_results = []
        for channel in channels:
            try:
                logger.info(f"Sending notification via {channel}")
                # In a production system, this would actually send notifications
                # For this demo, we'll simulate the notification
                
                # Simulate notification sending
                channel_result = simulate_notification(channel, client_id, alert)
                
                notification_results.append({
                    'channel': channel,
                    'success': channel_result.get('success', False),
                    'error': channel_result.get('error') if not channel_result.get('success', False) else None
                })
                
            except Exception as e:
                logger.error(f"Error sending notification via {channel}: {str(e)}")
                notification_results.append({
                    'channel': channel,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate success rate
        successful_channels = sum(1 for r in notification_results if r.get('success', False))
        all_channels = len(notification_results)
        success_rate = (successful_channels / all_channels) if all_channels > 0 else 0
        
        # Log the event
        log_event(client_id, {
            'event_type': 'alert_processed',
            'alert_type': alert_type,
            'severity': severity,
            'channels': channels,
            'successful_channels': successful_channels,
            'timestamp': datetime.utcnow().isoformat() + "Z"
        })
        
        # Calculate duration
        duration = time.time() - start_time
        
        return {
            'success': successful_channels > 0,  # Consider success if at least one channel worked
            'processed_alert': {
                'client_id': client_id,
                'alert_type': alert_type,
                'severity': severity,
                'channels': channels,
                'successful_channels': successful_channels,
                'success_rate': success_rate,
                'processing_time': duration
            },
            'notification_results': notification_results,
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error processing alert: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }

def determine_notification_channels(client_config, severity):
    """
    Determine which notification channels to use based on severity and client preferences.
    
    Args:
        client_config: Client configuration
        severity: Alert severity
        
    Returns:
        List of notification channels to use
    """
    # Get client's preferred channels
    preferred_channels = client_config.get('preferences', {}).get('notification_channels', ['app'])
    
    # Default channels based on severity
    if severity == 'critical':
        # For critical alerts, use all available channels
        return list(set(['app', 'sms', 'email', 'phone'] + preferred_channels))
    elif severity == 'high':
        # For high severity, use app, SMS, and email
        return list(set(['app', 'sms', 'email'] + preferred_channels))
    elif severity == 'medium':
        # For medium severity, use app and email
        return list(set(['app', 'email'] + preferred_channels))
    else:
        # For low severity, just use app and preferred channels
        return list(set(['app'] + preferred_channels))

def simulate_notification(channel, client_id, alert):
    """
    Simulate sending a notification via a specific channel.
    In a production system, this would actually send the notification.
    
    Args:
        channel: Notification channel
        client_id: Client identifier
        alert: Alert data
        
    Returns:
        Simulated notification result
    """
    # Add a small delay to simulate notification sending
    time.sleep(0.1)
    
    # Get endpoint for this channel from environment variable
    endpoint_key = f"{channel.upper()}_ENDPOINT"
    endpoint = os.environ.get(endpoint_key)
    
    if not endpoint:
        endpoint = os.environ.get('NOTIFICATION_ENDPOINT', 'https://example.com/notify')
    
    # In a production system, we would actually call the endpoint
    
    # Simulate random failure (5% chance)
    import random
    if random.random() < 0.05:
        return {
            'success': False,
            'error': f"Simulated failure for {channel} notification",
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
    
    return {
        'success': True,
        'channel': channel,
        'endpoint': endpoint,
        'timestamp': datetime.utcnow().isoformat() + "Z"
    }