import logging
import json
import time
import os
import uuid
from typing import Dict, List, Any, Optional, Callable
import threading
import boto3
from botocore.exceptions import ClientError

class RealtimeNotificationService:
    """
    Service for sending real-time notifications to caregivers and patients.
    Uses AWS SNS for pub/sub messaging and supports WebSocket integration.
    """
    
    def __init__(self):
        """Initialize the real-time notification service."""
        self.logger = logging.getLogger(__name__)
        
        # Active WebSocket connections
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.connection_lock = threading.Lock()
        
        # Connection groups for targeting specific users or roles
        self.connection_groups: Dict[str, List[str]] = {
            "all": [],
            "caregivers": [],
            "patients": []
        }
        
        # AWS SNS configuration
        self.use_sns = False
        self.sns_client = None
        self.sns_topic_arn = os.environ.get('NOTIFICATION_SNS_TOPIC_ARN')
        
        # Initialize SNS if configured
        if self.sns_topic_arn:
            try:
                self.sns_client = boto3.client('sns')
                self.use_sns = True
                self.logger.info(f"SNS notifications enabled using topic: {self.sns_topic_arn}")
            except Exception as e:
                self.logger.error(f"Failed to initialize SNS client: {str(e)}")
                self.use_sns = False
        
        # Message handlers
        self.message_handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        
        self.logger.info("Real-time notification service initialized")
    
    def register_connection(self, connection_id: str, user_data: Dict[str, Any]) -> None:
        """
        Register a new WebSocket connection.
        
        Args:
            connection_id: Unique WebSocket connection ID
            user_data: User data including type, id, etc.
        """
        with self.connection_lock:
            self.connections[connection_id] = {
                'user_data': user_data,
                'connected_at': time.time(),
                'last_activity': time.time()
            }
            
            # Add to 'all' group
            if connection_id not in self.connection_groups['all']:
                self.connection_groups['all'].append(connection_id)
            
            # Add to type-specific group
            user_type = user_data.get('type', '').lower()
            if user_type in ('caregiver', 'caregivers'):
                if connection_id not in self.connection_groups['caregivers']:
                    self.connection_groups['caregivers'].append(connection_id)
            elif user_type in ('patient', 'patients'):
                if connection_id not in self.connection_groups['patients']:
                    self.connection_groups['patients'].append(connection_id)
            
            # Add to user-specific group
            user_id = user_data.get('id')
            if user_id:
                group_name = f"user_{user_id}"
                if group_name not in self.connection_groups:
                    self.connection_groups[group_name] = []
                if connection_id not in self.connection_groups[group_name]:
                    self.connection_groups[group_name].append(connection_id)
        
        self.logger.info(f"WebSocket connection registered: {connection_id} ({user_type})")
    
    def unregister_connection(self, connection_id: str) -> None:
        """
        Unregister a WebSocket connection.
        
        Args:
            connection_id: Connection ID to unregister
        """
        with self.connection_lock:
            if connection_id in self.connections:
                del self.connections[connection_id]
            
            # Remove from all groups
            for group_name, connections in self.connection_groups.items():
                if connection_id in connections:
                    self.connection_groups[group_name].remove(connection_id)
        
        self.logger.info(f"WebSocket connection unregistered: {connection_id}")
    
    def update_connection_activity(self, connection_id: str) -> None:
        """
        Update last activity timestamp for a connection.
        
        Args:
            connection_id: Connection ID
        """
        with self.connection_lock:
            if connection_id in self.connections:
                self.connections[connection_id]['last_activity'] = time.time()
    
    def send_notification(self, notification: Dict[str, Any], target: Optional[str] = None) -> bool:
        """
        Send a notification to target connections or groups.
        
        Args:
            notification: Notification data to send
            target: Target specification, can be:
                   - None: Send to all connections
                   - 'caregivers': Send to all caregiver connections
                   - 'patients': Send to all patient connections
                   - 'user_<id>': Send to specific user connections
                   - '<connection_id>': Send to specific connection
            
        Returns:
            bool: Success of sending the notification
        """
        # Make sure notification has all required fields
        if 'type' not in notification:
            notification['type'] = 'general'
        if 'timestamp' not in notification:
            notification['timestamp'] = time.time()
        if 'id' not in notification:
            notification['id'] = str(uuid.uuid4())
        
        # Send via SNS if enabled (broadcast to all subscribers)
        if self.use_sns and self.sns_client and not target:
            try:
                self.sns_client.publish(
                    TopicArn=self.sns_topic_arn,
                    Message=json.dumps(notification),
                    MessageAttributes={
                        'NotificationType': {
                            'DataType': 'String',
                            'StringValue': notification.get('type', 'general')
                        }
                    }
                )
                self.logger.debug(f"Notification published to SNS: {notification['id']}")
                return True
            except Exception as e:
                self.logger.error(f"Error publishing to SNS: {str(e)}")
                # Fall back to direct WebSocket delivery
        
        # Get target connection IDs
        target_connections = []
        
        with self.connection_lock:
            if not target or target == 'all':
                # Send to all connections
                target_connections = list(self.connections.keys())
            elif target in self.connection_groups:
                # Send to a specific group
                target_connections = self.connection_groups[target]
            elif target in self.connections:
                # Send to a specific connection
                target_connections = [target]
            else:
                # Try to parse as user ID
                user_group = f"user_{target}"
                if user_group in self.connection_groups:
                    target_connections = self.connection_groups[user_group]
        
        # Send the notification to each target connection
        # Note: In a real implementation, this would use API Gateway WebSocket API
        # to send messages to each connection. For now, we'll just log the intent.
        for conn_id in target_connections:
            if conn_id in self.connections:
                self.logger.debug(f"Would send notification to connection {conn_id}: {notification['id']}")
                # In a real implementation:
                # api_gateway.post_to_connection(
                #     ConnectionId=conn_id,
                #     Data=json.dumps(notification)
                # )
        
        if target_connections:
            self.logger.info(f"Notification {notification['id']} sent to {len(target_connections)} connections")
            return True
        else:
            self.logger.warning(f"No connections found for target: {target}")
            return False
    
    def register_message_handler(self, message_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Function to call with message
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        
        self.message_handlers[message_type].append(handler)
        self.logger.debug(f"Registered handler for message type: {message_type}")
    
    def handle_incoming_message(self, connection_id: str, message: Dict[str, Any]) -> None:
        """
        Handle an incoming message from a WebSocket connection.
        
        Args:
            connection_id: Connection ID
            message: Message data
        """
        # Update connection activity
        self.update_connection_activity(connection_id)
        
        # Get message type
        message_type = message.get('type', 'unknown')
        
        # Add metadata to message
        message['connection_id'] = connection_id
        if connection_id in self.connections:
            message['user_data'] = self.connections[connection_id].get('user_data', {})
        
        # Call handlers for this message type
        if message_type in self.message_handlers:
            for handler in self.message_handlers[message_type]:
                try:
                    handler(message)
                except Exception as e:
                    self.logger.error(f"Error in message handler for type {message_type}: {str(e)}")
        
        self.logger.debug(f"Processed message from {connection_id} of type {message_type}")
    
    def cleanup_stale_connections(self, max_idle_time: int = 300) -> None:
        """
        Clean up connections that haven't had activity for a while.
        
        Args:
            max_idle_time: Maximum idle time in seconds
        """
        current_time = time.time()
        connections_to_remove = []
        
        with self.connection_lock:
            for conn_id, conn_data in self.connections.items():
                if current_time - conn_data['last_activity'] > max_idle_time:
                    connections_to_remove.append(conn_id)
        
        for conn_id in connections_to_remove:
            self.unregister_connection(conn_id)
        
        if connections_to_remove:
            self.logger.info(f"Cleaned up {len(connections_to_remove)} stale connections")
    
    def subscribe_to_sns(self) -> bool:
        """
        Subscribe to SNS topic to receive messages.
        Used when running multiple server instances.
        
        Returns:
            bool: Success of subscription
        """
        if not self.use_sns or not self.sns_client:
            self.logger.warning("SNS not configured, cannot subscribe")
            return False
        
        try:
            # In a real implementation, this would set up an HTTP or SQS endpoint
            # that AWS SNS can deliver messages to
            self.logger.info(f"Would subscribe to SNS topic: {self.sns_topic_arn}")
            return True
        except Exception as e:
            self.logger.error(f"Error subscribing to SNS: {str(e)}")
            return False
    
    def create_alert_notification(self, alert_type: str, patient_id: str, message: str, 
                                 data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create an alert notification for caregivers.
        
        Args:
            alert_type: Type of alert (e.g., 'wandering', 'fall')
            patient_id: ID of the patient
            message: Alert message
            data: Additional data to include
            
        Returns:
            Notification object
        """
        notification = {
            'type': 'alert',
            'alert_type': alert_type,
            'patient_id': patient_id,
            'message': message,
            'timestamp': time.time(),
            'id': str(uuid.uuid4()),
            'priority': 'high'
        }
        
        if data:
            notification['data'] = data
        
        return notification
    
    def send_patient_alert(self, alert_type: str, patient_id: str, message: str, 
                          data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send an alert notification about a patient to caregivers.
        
        Args:
            alert_type: Type of alert (e.g., 'wandering', 'fall')
            patient_id: ID of the patient
            message: Alert message
            data: Additional data to include
            
        Returns:
            bool: Success of sending the alert
        """
        notification = self.create_alert_notification(alert_type, patient_id, message, data)
        
        # Send to caregivers and specific patient (so they see it on their device too)
        caregiver_success = self.send_notification(notification, 'caregivers')
        patient_success = self.send_notification(notification, f"user_{patient_id}")
        
        return caregiver_success or patient_success