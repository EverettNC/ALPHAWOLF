###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# UTILITY FUNCTIONS
# Common utility functions for logging, UUID generation, timestamping,
# and other shared functionality across the AlphaWolf system.
###############################################################################

import uuid
import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("alphawolf.utils")

def generate_uuid() -> str:
    """
    Generate a UUID for uniquely identifying entities
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())

def generate_session_id() -> str:
    """
    Generate a session ID for tracking user interactions
    
    Returns:
        Session ID string
    """
    return f"sess-{int(time.time())}-{uuid.uuid4().hex[:6]}"

def get_timestamp() -> str:
    """
    Get the current timestamp in ISO format
    
    Returns:
        ISO formatted timestamp
    """
    return datetime.utcnow().isoformat() + "Z"

def log_event(client_id: str, event_data: Dict[str, Any]) -> bool:
    """
    Log an event to the audit trail
    
    Args:
        client_id: Client identifier
        event_data: Event data to log
        
    Returns:
        Success status
    """
    try:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Determine log file path
        today = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = os.path.join(logs_dir, f"{today}_events.jsonl")
        
        # Create log entry
        log_entry = {
            "timestamp": get_timestamp(),
            "client_id": client_id,
            "event": event_data
        }
        
        # Append to log file
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Also log to application logger
        logger.info(f"Event logged for client {client_id}: {event_data.get('action', 'unknown')}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error logging event: {str(e)}")
        return False

def sanitize_input(text: str) -> str:
    """
    Sanitize user input for security
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially harmful characters
    sanitized = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # Limit length
    max_length = 1000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized

def load_client_data(client_id: str) -> Optional[Dict[str, Any]]:
    """
    Load client data from storage
    
    Args:
        client_id: Client identifier
        
    Returns:
        Client data or None if not found
    """
    try:
        clients_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'clients.json')
        
        if not os.path.exists(clients_file):
            return None
        
        with open(clients_file, 'r') as f:
            clients = json.load(f)
        
        return next((client for client in clients if client.get('client_id') == client_id), None)
    
    except Exception as e:
        logger.error(f"Error loading client data: {str(e)}")
        return None

def save_client_data(client_data: Dict[str, Any]) -> bool:
    """
    Save client data to storage
    
    Args:
        client_data: Client data to save
        
    Returns:
        Success status
    """
    try:
        clients_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'clients.json')
        
        # Create file if it doesn't exist
        if not os.path.exists(clients_file):
            with open(clients_file, 'w') as f:
                json.dump([], f)
        
        # Load existing clients
        with open(clients_file, 'r') as f:
            clients = json.load(f)
        
        # Update or add client
        client_id = client_data.get('client_id')
        for i, client in enumerate(clients):
            if client.get('client_id') == client_id:
                clients[i] = client_data
                break
        else:
            clients.append(client_data)
        
        # Save updated clients
        with open(clients_file, 'w') as f:
            json.dump(clients, f, indent=2)
        
        return True
    
    except Exception as e:
        logger.error(f"Error saving client data: {str(e)}")
        return False