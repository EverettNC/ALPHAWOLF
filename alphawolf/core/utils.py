###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# UTILITY FUNCTIONS
# Common utility functions used across the AlphaWolf system.
###############################################################################

import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def generate_session_id() -> str:
    """
    Generate a unique session ID.
    
    Returns:
        Unique session ID string
    """
    # Create a UUID and use the hex representation without hyphens
    return str(uuid.uuid4()).replace('-', '')

def log_event(client_id: str, event_data: Dict[str, Any]) -> bool:
    """
    Log an event to the event store.
    
    Args:
        client_id: Client identifier
        event_data: Event data to log
        
    Returns:
        True if logging was successful
    """
    try:
        # Add timestamp if not present
        if 'timestamp' not in event_data:
            event_data['timestamp'] = datetime.utcnow().isoformat() + "Z"
        
        # Add client ID to event data
        event_data['client_id'] = client_id
        
        # In a production system, this would write to a database or event stream
        # For this demo, we'll write to a log file
        
        # Get log directory
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'event_logs'
        )
        
        # Ensure directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log filename based on client ID and date
        date_part = datetime.utcnow().strftime('%Y%m%d')
        log_file = os.path.join(log_dir, f"{client_id}_{date_part}.jsonl")
        
        # Write event to log file (append mode)
        with open(log_file, 'a') as f:
            f.write(json.dumps(event_data) + '\n')
        
        logger.debug(f"Logged event for client {client_id}: {event_data.get('event_type', 'unknown')}")
        return True
        
    except Exception as e:
        logger.error(f"Error logging event: {str(e)}")
        return False

def sanitize_input(input_text: str) -> str:
    """
    Sanitize input text to prevent security issues.
    
    Args:
        input_text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not input_text:
        return ''
    
    # Convert to string if not already
    text = str(input_text)
    
    # Limit length
    if len(text) > 10000:
        text = text[:10000]
    
    # Remove potentially dangerous characters
    # This is a basic implementation - production would use a proper sanitizer
    text = re.sub(r'[^\w\s.,!?:;()\[\]{}\'"-]', '', text)
    
    return text

def get_client_config(client_id: str) -> Dict[str, Any]:
    """
    Get configuration for a specific client.
    
    Args:
        client_id: Client identifier
        
    Returns:
        Client configuration
    """
    try:
        # In a production system, this would load from a database
        # For this demo, we'll check for a local file
        config_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'clients',
            f"{client_id}.json"
        )
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Return default configuration
            return {
                'client_id': client_id,
                'created_at': datetime.utcnow().isoformat() + "Z",
                'features': {
                    'risk_analysis': True,
                    'family_protection': True,
                    'location_tracking': True,
                    'web_content': True
                },
                'preferences': {
                    'alert_threshold': 70,
                    'safety_radius': 100,  # meters
                    'language': 'en',
                    'notification_channels': ['app', 'email']
                }
            }
        
    except Exception as e:
        logger.error(f"Error loading client config for {client_id}: {str(e)}")
        # Return minimal configuration
        return {
            'client_id': client_id,
            'error': str(e),
            'features': {
                'risk_analysis': True
            }
        }

def save_client_config(client_id: str, config: Dict[str, Any]) -> bool:
    """
    Save configuration for a specific client.
    
    Args:
        client_id: Client identifier
        config: Client configuration to save
        
    Returns:
        True if save was successful
    """
    try:
        # Create clients directory if it doesn't exist
        clients_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'clients'
        )
        
        os.makedirs(clients_dir, exist_ok=True)
        
        # Save config
        config_file = os.path.join(clients_dir, f"{client_id}.json")
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved configuration for client {client_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving client config for {client_id}: {str(e)}")
        return False

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    Format a timestamp in ISO8601 format with Z suffix.
    
    Args:
        timestamp: Timestamp to format, or None for current time
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    return timestamp.isoformat() + "Z"

def format_duration(seconds: float) -> str:
    """
    Format a duration in a human-readable way.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"