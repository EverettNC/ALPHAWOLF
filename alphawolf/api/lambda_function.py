"""
AlphaWolf Lambda Function Handler
Part of The Christman AI Project - LumaCognify AI

This module handles API Gateway events and orchestrates the AlphaWolf serverless backend.

"HOW CAN I HELP YOU LOVE YOURSELF MORE"
"""

import os
import json
import logging
import datetime
import uuid
import traceback
try:
    import boto3
    from boto3.dynamodb.conditions import Key, Attr
except ImportError:
    # Mock boto3 for local testing
    boto3 = None
try:
    import botocore.exceptions
except ImportError:
    # Mock botocore for local testing
    class botocore:
        class exceptions:
            ClientError = Exception

# Import local modules
try:
    from ..core.family_protection import FamilyProtectionSystem
    from ..core.web_crawler import WebCrawler
    # from ..core.risk_model import RiskAnalyzer  # Import when implemented
except ImportError:
    # When running as Lambda function
    try:
        from core.family_protection import FamilyProtectionSystem
        from core.web_crawler import WebCrawler
        # from core.risk_model import RiskAnalyzer  # Import when implemented
    except ImportError:
        # Fallback for local testing
        FamilyProtectionSystem = None
        WebCrawler = None
        # RiskAnalyzer = None

# Configure logging
logger = logging.getLogger(__name__)
log_level = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))

# Initialize services if running in AWS
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") and boto3:
    sqs_client = boto3.client('sns')
    dynamodb = boto3.resource('dynamodb')
    
    # Get table references from environment variables
    interactions_table_name = os.environ.get("INTERACTIONS_TABLE", "alphawolf-interactions")
    locations_table_name = os.environ.get("LOCATIONS_TABLE", "alphawolf-locations")
    content_table_name = os.environ.get("CONTENT_TABLE", "alphawolf-content")
    
    # Initialize DynamoDB tables
    interactions_table = dynamodb.Table(interactions_table_name)
    locations_table = dynamodb.Table(locations_table_name)
    content_table = dynamodb.Table(content_table_name)
    
    # Initialize SQS queue
    sqs_client = boto3.client('sqs')
    alert_queue_url = os.environ.get("ALERT_QUEUE_URL")
else:
    # Mock services for local testing
    sqs_client = None
    dynamodb = None
    interactions_table = None
    locations_table = None
    content_table = None
    alert_queue_url = None

# Initialize AlphaWolf core components
family_protection = FamilyProtectionSystem() if FamilyProtectionSystem else None
web_crawler = WebCrawler() if WebCrawler else None
# risk_analyzer = RiskAnalyzer() if RiskAnalyzer else None

def lambda_handler(event, context):
    """
    AWS Lambda handler for AlphaWolf API
    
    Parameters:
    - event: The Lambda event object
    - context: The Lambda context object
    
    Returns:
    - API Gateway response object
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Record request in interactions table if available
    request_id = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().isoformat()
    
    if interactions_table:
        try:
            # Store interaction record
            interaction_item = {
                "request_id": request_id,
                "timestamp": timestamp,
                "event_type": "api_request",
                "path": event.get("path", "unknown"),
                "method": event.get("httpMethod", "unknown"),
                "source_ip": event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown"),
                "user_agent": event.get("requestContext", {}).get("identity", {}).get("userAgent", "unknown"),
                "ttl": int(datetime.datetime.utcnow().timestamp() + 2592000)  # 30 days retention
            }
            
            # Add request body if present (and not a GET request)
            if event.get("httpMethod") != "GET" and event.get("body"):
                try:
                    body = json.loads(event.get("body", "{}"))
                    # Exclude sensitive fields
                    if "password" in body:
                        body["password"] = "***REDACTED***"
                    interaction_item["request_body"] = json.dumps(body)
                except (json.JSONDecodeError, TypeError):
                    # If body isn't valid JSON, store as string
                    interaction_item["request_body"] = event.get("body", "")[:1000]  # Limit size
                    
            interactions_table.put_item(Item=interaction_item)
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
    
    # Handle different API endpoints
    try:
        # Check if event is from API Gateway
        if "httpMethod" in event:
            return handle_api_gateway_event(event, request_id, timestamp)
        # Check if event is from SQS
        elif "Records" in event and event.get("Records", [{}])[0].get("eventSource") == "aws:sqs":
            return handle_sqs_event(event, request_id, timestamp)
        # Check if event is from CloudWatch Events
        elif "source" in event and event.get("source") == "aws.events":
            return handle_cloudwatch_event(event, request_id, timestamp)
        # Handle direct Lambda invocation
        else:
            return handle_direct_invocation(event, request_id, timestamp)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Record error in interactions table if available
        if interactions_table:
            try:
                error_item = {
                    "request_id": request_id,
                    "timestamp": timestamp,
                    "event_type": "error",
                    "error_message": str(e),
                    "error_traceback": traceback.format_exc(),
                    "ttl": int(datetime.datetime.utcnow().timestamp() + 2592000)  # 30 days retention
                }
                interactions_table.put_item(Item=error_item)
            except Exception as inner_e:
                logger.error(f"Error storing error record: {inner_e}")
        
        # Return error response
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e),
                "request_id": request_id
            })
        }

def handle_api_gateway_event(event, request_id, timestamp):
    """
    Handle API Gateway events
    
    Parameters:
    - event: The Lambda event object
    - request_id: Unique request ID
    - timestamp: Request timestamp
    
    Returns:
    - API Gateway response object
    """
    # Extract request information
    http_method = event.get("httpMethod", "")
    path = event.get("path", "")
    
    # Health check endpoint
    if path.endswith("/health") and http_method == "GET":
        # Simple health check that verifies AWS services connection
        health_status = "ok"
        services_status = {}
        
        # Check DynamoDB connection
        if dynamodb:
            try:
                # Test listTables to verify DynamoDB access
                dynamodb.meta.client.list_tables(Limit=1)
                services_status["dynamodb"] = "connected"
            except Exception as e:
                health_status = "degraded"
                services_status["dynamodb"] = f"error: {str(e)}"
        else:
            services_status["dynamodb"] = "not configured"
            
        # Check SQS connection
        if sqs_client and alert_queue_url:
            try:
                # Test queue attributes to verify SQS access
                sqs_client.get_queue_attributes(
                    QueueUrl=alert_queue_url,
                    AttributeNames=['QueueArn']
                )
                services_status["sqs"] = "connected"
            except Exception as e:
                health_status = "degraded"
                services_status["sqs"] = f"error: {str(e)}"
        else:
            services_status["sqs"] = "not configured"
        
        # Return health check response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": health_status,
                "timestamp": timestamp,
                "request_id": request_id,
                "services": services_status,
                "version": "1.0.0"
            })
        }
    
    # Parse request body for non-GET requests
    body = {}
    if http_method != "GET" and event.get("body"):
        try:
            body = json.loads(event.get("body", "{}"))
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Invalid JSON in request body",
                    "request_id": request_id
                })
            }
    
    # Handle family protection endpoints
    if path.endswith("/safety") and http_method == "POST":
        # Check required parameters
        required_params = ["latitude", "longitude", "user_id"]
        if not all(param in body for param in required_params):
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Missing required parameters",
                    "required": required_params,
                    "request_id": request_id
                })
            }
        
        # Call family protection system
        if family_protection:
            result = family_protection.check_location_safety(
                latitude=body["latitude"],
                longitude=body["longitude"],
                safety_zones=body.get("safety_zones", []),
                user_id=body["user_id"],
                timestamp=body.get("timestamp")
            )
            
            # Check for alert and send to SQS if needed
            if "alert" in result and sqs_client and alert_queue_url:
                try:
                    # Send alert to SQS queue
                    alert_message = {
                        "alert_type": "location",
                        "severity": result["alert"]["severity"],
                        "message": result["alert"]["message"],
                        "alert_id": result["alert"]["alert_id"],
                        "timestamp": result["alert"]["alert_timestamp"],
                        "location": {
                            "latitude": result["latitude"],
                            "longitude": result["longitude"]
                        },
                        "user_id": result["user_id"]
                    }
                    
                    sqs_client.send_message(
                        QueueUrl=alert_queue_url,
                        MessageBody=json.dumps(alert_message)
                    )
                    
                    result["alert"]["queued"] = True
                except Exception as e:
                    logger.error(f"Error sending alert to SQS: {e}")
                    result["alert"]["queued"] = False
                    result["alert"]["queue_error"] = str(e)
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(result)
            }
        else:
            return {
                "statusCode": 501,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Family protection system not available",
                    "request_id": request_id
                })
            }
    
    # Handle movement analysis endpoint
    elif path.endswith("/track") and http_method == "POST":
        # Check required parameters
        required_params = ["current_location", "user_id"]
        if not all(param in body for param in required_params):
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Missing required parameters",
                    "required": required_params,
                    "request_id": request_id
                })
            }
        
        # Call family protection system
        if family_protection:
            result = family_protection.detect_unusual_movement(
                current_location=body["current_location"],
                previous_locations=body.get("previous_locations", []),
                user_id=body["user_id"]
            )
            
            # Check for alert and send to SQS if needed
            if "alert" in result and sqs_client and alert_queue_url:
                try:
                    # Send alert to SQS queue
                    alert_message = {
                        "alert_type": "movement",
                        "severity": result["alert"]["severity"],
                        "message": result["alert"]["message"],
                        "alert_id": result["alert"]["alert_id"],
                        "timestamp": result["alert"]["alert_timestamp"],
                        "assessment": result["assessment"],
                        "user_id": result["user_id"]
                    }
                    
                    sqs_client.send_message(
                        QueueUrl=alert_queue_url,
                        MessageBody=json.dumps(alert_message)
                    )
                    
                    result["alert"]["queued"] = True
                except Exception as e:
                    logger.error(f"Error sending alert to SQS: {e}")
                    result["alert"]["queued"] = False
                    result["alert"]["queue_error"] = str(e)
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(result)
            }
        else:
            return {
                "statusCode": 501,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Family protection system not available",
                    "request_id": request_id
                })
            }
    
    # Handle content retrieval endpoint
    elif path.endswith("/content") and http_method == "GET":
        query_params = event.get("queryStringParameters", {}) or {}
        
        # Parse query parameters
        topic = query_params.get("topic")
        subtopics = query_params.get("subtopics", "").split(",") if query_params.get("subtopics") else None
        max_results = int(query_params.get("max_results", "10"))
        
        if not topic:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Missing required parameter: topic",
                    "request_id": request_id
                })
            }
        
        # Call web crawler
        if web_crawler:
            results = web_crawler.search_topic(
                topic=topic,
                subtopics=subtopics,
                max_results=max_results
            )
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "topic": topic,
                    "subtopics": subtopics,
                    "count": len(results),
                    "results": results,
                    "request_id": request_id
                })
            }
        else:
            return {
                "statusCode": 501,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Web crawler not available",
                    "request_id": request_id
                })
            }
    
    # Handle research retrieval endpoint
    elif path.endswith("/research") and http_method == "GET":
        query_params = event.get("queryStringParameters", {}) or {}
        
        # Parse query parameters
        condition = query_params.get("condition")
        max_results = int(query_params.get("max_results", "5"))
        max_age_days = int(query_params.get("max_age_days", "90"))
        
        if not condition:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Missing required parameter: condition",
                    "request_id": request_id
                })
            }
        
        # Call web crawler
        if web_crawler:
            results = web_crawler.get_latest_research(
                condition=condition,
                max_results=max_results,
                max_age_days=max_age_days
            )
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "condition": condition,
                    "count": len(results),
                    "results": results,
                    "request_id": request_id
                })
            }
        else:
            return {
                "statusCode": 501,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Web crawler not available",
                    "request_id": request_id
                })
            }
    
    # Handle CORS preflight requests
    elif http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
            },
            "body": ""
        }
    
    # Handle unsupported endpoint
    else:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Endpoint not found",
                "path": path,
                "method": http_method,
                "request_id": request_id
            })
        }

def handle_sqs_event(event, request_id, timestamp):
    """
    Handle SQS events
    
    Parameters:
    - event: The Lambda event object
    - request_id: Unique request ID
    - timestamp: Request timestamp
    
    Returns:
    - Success response
    """
    # Process each SQS record
    for record in event.get("Records", []):
        try:
            # Parse message body
            body = json.loads(record.get("body", "{}"))
            
            # Store in interactions table
            if interactions_table:
                try:
                    interaction_item = {
                        "request_id": request_id,
                        "timestamp": timestamp,
                        "event_type": "sqs_message",
                        "message_body": json.dumps(body),
                        "message_id": record.get("messageId", "unknown"),
                        "ttl": int(datetime.datetime.utcnow().timestamp() + 2592000)  # 30 days retention
                    }
                    interactions_table.put_item(Item=interaction_item)
                except Exception as e:
                    logger.error(f"Error storing SQS interaction: {e}")
            
            # Handle different message types
            alert_type = body.get("alert_type")
            
            if alert_type == "location":
                if family_protection:
                    # Process location alert
                    logger.info(f"Processing location alert for user: {body.get('user_id')}")
                    # Additional processing would go here
                    pass
            elif alert_type == "movement":
                if family_protection:
                    # Process movement alert
                    logger.info(f"Processing movement alert for user: {body.get('user_id')}")
                    # Additional processing would go here
                    pass
            elif alert_type == "communication":
                # Process communication alert
                logger.info(f"Processing communication alert for user: {body.get('user_id')}")
                # Additional processing would go here
                pass
            else:
                logger.warning(f"Unknown alert type: {alert_type}")
        except Exception as e:
            logger.error(f"Error processing SQS record: {e}")
            logger.error(traceback.format_exc())
    
    return {
        "statusCode": 200,
        "body": f"Processed {len(event.get('Records', []))} SQS messages"
    }

def handle_cloudwatch_event(event, request_id, timestamp):
    """
    Handle CloudWatch scheduled events
    
    Parameters:
    - event: The Lambda event object
    - request_id: Unique request ID
    - timestamp: Request timestamp
    
    Returns:
    - Success response
    """
    # Store event in interactions table
    if interactions_table:
        try:
            interaction_item = {
                "request_id": request_id,
                "timestamp": timestamp,
                "event_type": "scheduled_event",
                "event_details": json.dumps(event),
                "ttl": int(datetime.datetime.utcnow().timestamp() + 2592000)  # 30 days retention
            }
            interactions_table.put_item(Item=interaction_item)
        except Exception as e:
            logger.error(f"Error storing scheduled event interaction: {e}")
    
    # Check event type from detail-type
    detail_type = event.get("detail-type", "")
    
    if detail_type == "Scheduled Event":
        # Periodic maintenance tasks
        logger.info("Running scheduled maintenance tasks")
        
        # Example: Clear old cache entries
        if web_crawler:
            logger.info("Refreshing web crawler cache...")
            # Additional tasks would go here
            pass
    
    return {
        "statusCode": 200,
        "body": "Processed CloudWatch event"
    }

def handle_direct_invocation(event, request_id, timestamp):
    """
    Handle direct Lambda invocation
    
    Parameters:
    - event: The Lambda event object
    - request_id: Unique request ID
    - timestamp: Request timestamp
    
    Returns:
    - Response object
    """
    # Store event in interactions table
    if interactions_table:
        try:
            interaction_item = {
                "request_id": request_id,
                "timestamp": timestamp,
                "event_type": "direct_invocation",
                "event_details": json.dumps(event),
                "ttl": int(datetime.datetime.utcnow().timestamp() + 2592000)  # 30 days retention
            }
            interactions_table.put_item(Item=interaction_item)
        except Exception as e:
            logger.error(f"Error storing direct invocation interaction: {e}")
    
    # Extract action from event
    action = event.get("action", "")
    
    if action == "check_location_safety":
        # Check location safety
        if family_protection:
            return family_protection.check_location_safety(
                latitude=event.get("latitude"),
                longitude=event.get("longitude"),
                safety_zones=event.get("safety_zones", []),
                user_id=event.get("user_id"),
                timestamp=event.get("timestamp")
            )
        else:
            return {"error": "Family protection system not available"}
    
    elif action == "analyze_unusual_movement":
        # Analyze unusual movement
        if family_protection:
            return family_protection.detect_unusual_movement(
                current_location=event.get("current_location", {}),
                previous_locations=event.get("previous_locations", []),
                user_id=event.get("user_id")
            )
        else:
            return {"error": "Family protection system not available"}
    
    elif action == "search_topic":
        # Search for content on a topic
        if web_crawler:
            return web_crawler.search_topic(
                topic=event.get("topic", ""),
                subtopics=event.get("subtopics"),
                max_results=event.get("max_results", 10)
            )
        else:
            return {"error": "Web crawler not available"}
    
    elif action == "get_research":
        # Get latest research
        if web_crawler:
            return web_crawler.get_latest_research(
                condition=event.get("condition", ""),
                max_results=event.get("max_results", 5),
                max_age_days=event.get("max_age_days", 90)
            )
        else:
            return {"error": "Web crawler not available"}
    
    else:
        return {
            "error": "Unknown action",
            "request_id": request_id
        }

# For local testing
if __name__ == "__main__":
    # Mock API Gateway event for testing
    api_event = {
        "httpMethod": "GET",
        "path": "/health",
        "headers": {
            "Content-Type": "application/json"
        },
        "queryStringParameters": {},
        "requestContext": {
            "identity": {
                "sourceIp": "127.0.0.1",
                "userAgent": "python-test"
            }
        }
    }
    
    # Test health check
    response = lambda_handler(api_event, None)
    print(f"Health check response: {json.dumps(response, indent=2)}")
    
    # Test location safety
    api_event = {
        "httpMethod": "POST",
        "path": "/safety",
        "body": json.dumps({
            "latitude": 37.7749,
            "longitude": -122.4194,
            "user_id": "test_user",
            "safety_zones": [
                {
                    "name": "Home",
                    "center": {"latitude": 37.7749, "longitude": -122.4194},
                    "radius": 200  # meters
                }
            ]
        })
    }
    
    # Only test if family protection is available
    if family_protection:
        response = lambda_handler(api_event, None)
        print(f"Location safety response: {json.dumps(response, indent=2)}")
    else:
        print("Family protection system not available for testing")