import logging
import json
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class CaregiverService:
    """Service for managing caregiver notifications and alerts."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_history = {}  # Store recent alerts by patient_id
        self.mqtt_client = None  # Would be initialized for real-time alerts
        self.logger.info("Caregiver service initialized")
    
    def notify_caregivers(self, alert):
        """
        Send alert notification to associated caregivers.
        
        Args:
            alert: Alert object with patient_id, alert_type, message
            
        Returns:
            bool: Success of notification
        """
        try:
            patient_id = alert.patient_id
            
            # Store alert in history
            if patient_id not in self.alert_history:
                self.alert_history[patient_id] = []
            
            # Add to history, keeping only last 20 alerts
            self.alert_history[patient_id].append({
                'alert_id': alert.id,
                'type': alert.alert_type,
                'message': alert.message,
                'timestamp': datetime.utcnow().isoformat(),
                'resolved': False
            })
            
            if len(self.alert_history[patient_id]) > 20:
                self.alert_history[patient_id].pop(0)
            
            # Log the alert
            self.logger.info(f"Alert for patient {patient_id}: {alert.alert_type} - {alert.message}")
            
            # In a real implementation, this would send push notifications, emails, or SMS
            # For now, we'll just simulate the notification process
            self._simulate_notification(alert)
            
            return True
        except Exception as e:
            self.logger.error(f"Error notifying caregivers: {str(e)}")
            return False
    
    def _simulate_notification(self, alert):
        """
        Simulate sending notifications through various channels.
        In a real implementation, this would use actual notification services.
        
        Args:
            alert: Alert object
        """
        # Simulate a console notification
        notification_message = f"ALERT: {alert.alert_type.upper()} - Patient {alert.patient_id} - {alert.message}"
        self.logger.warning(notification_message)
        
        # Simulate logging to a notification file
        try:
            with open('notification_log.txt', 'a') as f:
                f.write(f"{datetime.utcnow().isoformat()} - {notification_message}\n")
        except:
            pass
        
        # If MQTT was set up, this would publish to an alert topic
        if self.mqtt_client:
            try:
                # Convert alert to JSON
                alert_data = {
                    'alert_id': alert.id,
                    'patient_id': alert.patient_id,
                    'alert_type': alert.alert_type,
                    'message': alert.message,
                    'latitude': alert.latitude,
                    'longitude': alert.longitude,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Publish to MQTT topic
                # self.mqtt_client.publish(f"alphawolf/alerts/{alert.patient_id}", json.dumps(alert_data))
                self.logger.info(f"Would publish to MQTT: {json.dumps(alert_data)}")
            except Exception as e:
                self.logger.error(f"Error publishing to MQTT: {str(e)}")
    
    def get_alert_history(self, patient_id=None, limit=20):
        """
        Get recent alert history for a patient or all patients.
        
        Args:
            patient_id: Optional patient ID to filter by
            limit: Maximum number of alerts to return
            
        Returns:
            list: Recent alerts
        """
        all_alerts = []
        
        if patient_id:
            # Get alerts for specific patient
            if patient_id in self.alert_history:
                all_alerts = self.alert_history[patient_id][-limit:]
        else:
            # Get alerts for all patients
            for p_id, alerts in self.alert_history.items():
                # Add patient_id to each alert
                for alert in alerts:
                    alert_copy = alert.copy()
                    alert_copy['patient_id'] = p_id
                    all_alerts.append(alert_copy)
            
            # Sort by timestamp (newest first) and limit
            all_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
            all_alerts = all_alerts[:limit]
        
        return all_alerts
    
    def resolve_alert(self, alert_id, db_session=None):
        """
        Mark an alert as resolved.
        
        Args:
            alert_id: ID of the alert to resolve
            db_session: Optional database session
            
        Returns:
            bool: Success of resolution
        """
        try:
            if db_session is None:
                # If no session provided, assume we're in app context
                from app import db
                db_session = db.session
            
            from models import Alert
            
            # Update alert in database
            alert = db_session.query(Alert).get(alert_id)
            if alert:
                alert.is_resolved = True
                db_session.commit()
                
                # Update in memory cache if present
                patient_id = alert.patient_id
                if patient_id in self.alert_history:
                    for stored_alert in self.alert_history[patient_id]:
                        if stored_alert.get('alert_id') == alert_id:
                            stored_alert['resolved'] = True
                            break
                
                self.logger.info(f"Resolved alert {alert_id}")
                return True
            else:
                self.logger.warning(f"Alert {alert_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error resolving alert: {str(e)}")
            return False
    
    def get_patient_status_summary(self, patient_id, db_session=None):
        """
        Get a summary of patient status for caregiver dashboard.
        
        Args:
            patient_id: ID of the patient
            db_session: Optional database session
            
        Returns:
            dict: Patient status summary
        """
        try:
            if db_session is None:
                # If no session provided, assume we're in app context
                from app import db
                db_session = db.session
            
            from models import Patient, Alert, ExerciseResult, CognitiveProfile, SafeZone
            
            patient = db_session.query(Patient).get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Get recent alerts
            recent_alerts = db_session.query(Alert)\
                .filter_by(patient_id=patient_id, is_resolved=False)\
                .order_by(Alert.timestamp.desc())\
                .limit(5)\
                .all()
            
            # Get latest location
            current_location = None
            if patient.last_latitude and patient.last_longitude:
                current_location = {
                    'latitude': patient.last_latitude,
                    'longitude': patient.last_longitude,
                    'timestamp': patient.last_location_update
                }
                
                # Check if in a safe zone
                safe_zones = db_session.query(SafeZone).all()
                in_safe_zone = False
                zone_name = None
                
                from services.geolocation_service import GeolocationService
                geo_service = GeolocationService()
                
                for zone in safe_zones:
                    result = geo_service.is_in_safe_zone(
                        patient.last_latitude, 
                        patient.last_longitude,
                        [{'name': zone.name, 'latitude': zone.latitude, 'longitude': zone.longitude, 'radius': zone.radius}]
                    )
                    if result[0]:
                        in_safe_zone = True
                        zone_name = result[1]
                        break
                
                current_location['in_safe_zone'] = in_safe_zone
                current_location['zone_name'] = zone_name
            
            # Get cognitive profile
            profile = db_session.query(CognitiveProfile).filter_by(patient_id=patient_id).first()
            
            # Get recent exercise performance
            recent_results = db_session.query(ExerciseResult)\
                .filter_by(patient_id=patient_id)\
                .order_by(ExerciseResult.timestamp.desc())\
                .limit(5)\
                .all()
            
            avg_score = None
            if recent_results:
                avg_score = sum(r.score for r in recent_results) / len(recent_results)
            
            return {
                'patient_name': patient.name,
                'patient_id': patient.id,
                'alerts': [
                    {
                        'id': alert.id,
                        'type': alert.alert_type,
                        'message': alert.message,
                        'timestamp': alert.timestamp.isoformat()
                    } for alert in recent_alerts
                ],
                'location': current_location,
                'cognitive_profile': {
                    'memory': profile.memory_score if profile else 0,
                    'attention': profile.attention_score if profile else 0,
                    'language': profile.language_score if profile else 0,
                    'pattern': profile.pattern_recognition_score if profile else 0,
                    'problem': profile.problem_solving_score if profile else 0
                } if profile else None,
                'recent_performance': {
                    'avg_score': avg_score,
                    'exercise_count': len(recent_results),
                    'last_exercise': recent_results[0].timestamp.isoformat() if recent_results else None
                }
            }
                
        except Exception as e:
            self.logger.error(f"Error getting patient status: {str(e)}")
            return {'error': f"Could not retrieve patient status: {str(e)}"}
