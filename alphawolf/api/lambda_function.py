###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# LAMBDA FUNCTION HANDLER
# Main entry point for serverless functions, handling risk assessment,
# escalation logic, and client management.
###############################################################################

import json
import sys
import os

# Add core directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))

from risk_model import analyze_input
from utils import log_event, generate_session_id, get_timestamp

def lambda_handler(event, context):
    """
    Main handler for serverless function calls
    
    Args:
        event: The event data containing input text and client information
        context: AWS Lambda context (unused)
        
    Returns:
        Dictionary with status code and response body
    """
    user_input = event.get("input", "")
    client_id = event.get("client_id", "anonymous")
    session_id = event.get("session_id", generate_session_id())
    
    # Analyze the input for risk factors
    risk = analyze_input(user_input)
    
    # Determine if escalation is needed
    escalated = risk["score"] >= 85
    escalation_action = "AlphaOmegaNotified" if escalated else "Normal"
    
    # Prepare result
    result = {
        "client_id": client_id,
        "session_id": session_id,
        "input": user_input,
        "risk_score": risk["score"],
        "risk_factors": risk.get("factors", []),
        "escalated": escalated,
        "timestamp": get_timestamp(),
        "escalation_action": escalation_action
    }
    
    # Log the event for audit trails
    log_event(client_id, result)
    
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }

# For local testing
if __name__ == "__main__":
    test_event = {
        "client_id": "test-client-001",
        "input": "I feel very sad today, but I'm managing."
    }
    
    response = lambda_handler(test_event, None)
    print(json.dumps(response, indent=2))