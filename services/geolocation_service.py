# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com

import logging
import math
import json
import os
from datetime import datetime, timedelta
from geopy.distance import geodesic
from flask import current_app
from models import SafeZone, Alert, db

logger = logging.getLogger(__name__)

class GeolocationService:
    """Service for tracking patient location and detecting wandering beyond safe zones."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.location_history_dir = os.path.join('data', 'location_history')
        
        # Ensure location history directory exists
        os.makedirs(self.location_history_dir, exist_ok=True)
        
        # Default alert thresholds
        self.alert_thresholds = {
            'distance_threshold': 20,      # Meters beyond safe zone to trigger alert
            'speed_threshold': 3.0,        # m/s (roughly walking/slow jog pace)
            'time_threshold': 300,         # Seconds outside safe zone before alert
            'critical_distance': 500,      # Meters from any safe zone to trigger critical alert
            'alert_cooldown': 600          # Seconds between repeated alerts
        }
        
        self.logger.info("Geolocation service initialized")
    
    def update_patient_location(self, patient_id, latitude, longitude, timestamp=None):
        """
        Update a patient's current location.
        
        Args:
            patient_id: ID of the patient
            latitude: Current latitude
            longitude: Current longitude
            timestamp: Optional timestamp string (ISO format)
            
        Returns:
            dict: Result of location update with safety status
        """
        try:
            from models import Patient
            
            # Get current timestamp if not provided
            if timestamp is None:
                timestamp = datetime.utcnow().isoformat()
            else:
                # Ensure timestamp is in string format
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.isoformat()
            
            # Get patient from database
            patient = Patient.query.get(patient_id)
            if not patient:
                return {
                    'success': False,
                    'error': f"Patient with ID {patient_id} not found",
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Get previous location for calculating movement
            prev_latitude = patient.last_latitude
            prev_longitude = patient.last_longitude
            prev_update_time = patient.last_location_update
            
            # Update patient location in database
            patient.last_latitude = latitude
            patient.last_longitude = longitude
            patient.last_location_update = datetime.utcnow()
            db.session.commit()
            
            # Log location history
            self._log_location(patient_id, latitude, longitude, timestamp)
            
            # Check if patient is within safe zones
            safety_status = self.check_safe_zones(patient_id, latitude, longitude)
            
            # Calculate speed if previous location exists
            speed = None
            if prev_latitude and prev_longitude and prev_update_time:
                time_diff = (datetime.utcnow() - prev_update_time).total_seconds()
                if time_diff > 0:
                    distance = self._calculate_distance(
                        prev_latitude, prev_longitude, latitude, longitude
                    )
                    speed = distance / time_diff  # m/s
            
            return {
                'success': True,
                'patient_id': patient_id,
                'latitude': latitude,
                'longitude': longitude,
                'timestamp': timestamp,
                'safety_status': safety_status,
                'speed': speed,
                'previous_location': {
                    'latitude': prev_latitude,
                    'longitude': prev_longitude,
                    'timestamp': prev_update_time.isoformat() if prev_update_time else None
                } if prev_latitude and prev_longitude else None
            }
        except Exception as e:
            self.logger.error(f"Error updating patient location: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def check_safe_zones(self, patient_id, latitude, longitude):
        """
        Check if a location is within any defined safe zones.
        
        Args:
            patient_id: ID of the patient (for alert generation)
            latitude: Location latitude to check
            longitude: Location longitude to check
            
        Returns:
            dict: Safety status with zones and distances
        """
        try:
            # Get all safe zones from database
            safe_zones = SafeZone.query.all()
            
            if not safe_zones:
                self.logger.warning("No safe zones defined in the system")
                return {
                    'is_safe': False,
                    'closest_zone': None,
                    'distance_to_closest': float('inf'),
                    'inside_zones': [],
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Check each zone
            inside_zones = []
            closest_zone = None
            min_distance = float('inf')
            
            for zone in safe_zones:
                distance = self._calculate_distance(
                    zone.latitude, zone.longitude, latitude, longitude
                )
                
                if distance < min_distance:
                    min_distance = distance
                    closest_zone = {
                        'id': zone.id,
                        'name': zone.name,
                        'latitude': zone.latitude,
                        'longitude': zone.longitude,
                        'radius': zone.radius
                    }
                
                # Check if inside zone (distance less than radius)
                if distance <= zone.radius:
                    inside_zones.append({
                        'id': zone.id,
                        'name': zone.name,
                        'distance': distance
                    })
            
            # Determine if location is safe (inside any zone)
            is_safe = len(inside_zones) > 0
            
            # Create alert if outside all safe zones and distance is significant
            if not is_safe and min_distance > self.alert_thresholds['distance_threshold']:
                self._create_wandering_alert(patient_id, latitude, longitude, min_distance)
            
            return {
                'is_safe': is_safe,
                'closest_zone': closest_zone,
                'distance_to_closest': min_distance,
                'inside_zones': inside_zones,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error checking safe zones: {str(e)}")
            return {
                'is_safe': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def add_safe_zone(self, name, latitude, longitude, radius):
        """
        Add a new safe zone.
        
        Args:
            name: Name of the safe zone
            latitude: Center latitude
            longitude: Center longitude
            radius: Radius in meters
            
        Returns:
            dict: Result of operation
        """
        try:
            # Create new safe zone
            new_zone = SafeZone()
            new_zone.name = name
            new_zone.latitude = latitude
            new_zone.longitude = longitude
            new_zone.radius = radius
            
            # Save to database
            db.session.add(new_zone)
            db.session.commit()
            
            self.logger.info(f"Added new safe zone '{name}' with radius {radius}m")
            
            return {
                'success': True,
                'zone_id': new_zone.id,
                'name': name,
                'center': {'latitude': latitude, 'longitude': longitude},
                'radius': radius
            }
        except Exception as e:
            self.logger.error(f"Error adding safe zone: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_safe_zone(self, zone_id, name=None, latitude=None, longitude=None, radius=None):
        """
        Update an existing safe zone.
        
        Args:
            zone_id: ID of the zone to update
            name: Optional new name
            latitude: Optional new center latitude
            longitude: Optional new center longitude
            radius: Optional new radius in meters
            
        Returns:
            dict: Result of operation
        """
        try:
            # Get zone from database
            zone = SafeZone.query.get(zone_id)
            if not zone:
                return {
                    'success': False,
                    'error': f"Safe zone with ID {zone_id} not found"
                }
            
            # Update fields if provided
            if name is not None:
                zone.name = name
            if latitude is not None:
                zone.latitude = latitude
            if longitude is not None:
                zone.longitude = longitude
            if radius is not None:
                zone.radius = radius
            
            # Save to database
            db.session.commit()
            
            self.logger.info(f"Updated safe zone {zone_id}")
            
            return {
                'success': True,
                'zone_id': zone.id,
                'name': zone.name,
                'center': {'latitude': zone.latitude, 'longitude': zone.longitude},
                'radius': zone.radius
            }
        except Exception as e:
            self.logger.error(f"Error updating safe zone: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_safe_zone(self, zone_id):
        """
        Delete a safe zone.
        
        Args:
            zone_id: ID of the zone to delete
            
        Returns:
            dict: Result of operation
        """
        try:
            # Get zone from database
            zone = SafeZone.query.get(zone_id)
            if not zone:
                return {
                    'success': False,
                    'error': f"Safe zone with ID {zone_id} not found"
                }
            
            # Delete from database
            db.session.delete(zone)
            db.session.commit()
            
            self.logger.info(f"Deleted safe zone {zone_id}")
            
            return {
                'success': True,
                'zone_id': zone_id
            }
        except Exception as e:
            self.logger.error(f"Error deleting safe zone: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_safe_zones(self):
        """
        Get all defined safe zones.
        
        Returns:
            list: Safe zones
        """
        try:
            # Get all zones from database
            zones = SafeZone.query.all()
            
            # Convert to list of dicts
            result = []
            for zone in zones:
                result.append({
                    'id': zone.id,
                    'name': zone.name,
                    'latitude': zone.latitude,
                    'longitude': zone.longitude,
                    'radius': zone.radius,
                    'created_at': zone.created_at.isoformat() if zone.created_at else None
                })
            
            return result
        except Exception as e:
            self.logger.error(f"Error getting safe zones: {str(e)}")
            return []
    
    def get_patient_location_history(self, patient_id, limit=100):
        """
        Get location history for a patient.
        
        Args:
            patient_id: ID of the patient
            limit: Maximum number of locations to return
            
        Returns:
            list: Location history
        """
        try:
            # Get history file path
            history_file = os.path.join(self.location_history_dir, f"{patient_id}.json")
            
            if not os.path.exists(history_file):
                return []
            
            # Read history from file
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Return most recent entries up to limit
            return history[-limit:] if limit > 0 else history
        except Exception as e:
            self.logger.error(f"Error getting location history: {str(e)}")
            return []
    
    def _log_location(self, patient_id, latitude, longitude, timestamp):
        """Log a location update to the patient's history file."""
        try:
            # Create location entry
            location = {
                'timestamp': timestamp,
                'latitude': latitude,
                'longitude': longitude
            }
            
            # Get history file path
            history_file = os.path.join(self.location_history_dir, f"{patient_id}.json")
            
            # Load existing history or create new
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    try:
                        history = json.load(f)
                    except json.JSONDecodeError:
                        history = []
            else:
                history = []
            
            # Add new location
            history.append(location)
            
            # Limit history size (keep last 1000 entries)
            if len(history) > 1000:
                history = history[-1000:]
            
            # Save updated history
            with open(history_file, 'w') as f:
                json.dump(history, f)
        except Exception as e:
            self.logger.error(f"Error logging location: {str(e)}")
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in meters."""
        try:
            # Use geodesic distance (more accurate than Haversine)
            return geodesic((lat1, lon1), (lat2, lon2)).meters
        except Exception as e:
            self.logger.error(f"Error calculating distance: {str(e)}")
            
            # Fallback to Haversine formula if geodesic fails
            R = 6371000  # Earth radius in meters
            
            # Convert to radians
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            # Haversine formula
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            return distance
    
    def _create_wandering_alert(self, patient_id, latitude, longitude, distance):
        """Create an alert for a wandering patient."""
        try:
            # Get patient
            from models import Patient
            patient = Patient.query.get(patient_id)
            
            if not patient:
                self.logger.error(f"Patient with ID {patient_id} not found for alert")
                return
            
            # Check if there's already a recent wandering alert (to avoid spam)
            recent_alert = Alert.query.filter(
                Alert.patient_id == patient_id,
                Alert.alert_type == 'wandering',
                Alert.is_resolved == False,
                Alert.timestamp > datetime.utcnow() - timedelta(seconds=self.alert_thresholds['alert_cooldown'])
            ).first()
            
            if recent_alert:
                # Update existing alert with new location
                recent_alert.latitude = latitude
                recent_alert.longitude = longitude
                recent_alert.message = f"{patient.name} is {int(distance)}m outside of safe zones"
                db.session.commit()
                self.logger.info(f"Updated existing wandering alert for patient {patient_id}")
                return
            
            # Create new alert
            alert_message = f"{patient.name} is outside of all safe zones"
            
            # Determine severity based on distance
            if distance > self.alert_thresholds['critical_distance']:
                alert_message = f"CRITICAL: {patient.name} is {int(distance)}m outside of safe zones"
            else:
                alert_message = f"{patient.name} is {int(distance)}m outside of safe zones"
            
            new_alert = Alert()
            new_alert.patient_id = patient_id
            new_alert.alert_type = 'wandering'
            new_alert.message = alert_message
            new_alert.latitude = latitude
            new_alert.longitude = longitude
            
            # Save to database
            db.session.add(new_alert)
            db.session.commit()
            
            self.logger.info(f"Created wandering alert for patient {patient_id}: {alert_message}")
            
            # Notify caregivers (through caregiver service)
            try:
                from app import caregiver_service
                caregiver_service.notify_caregivers(new_alert)
            except Exception as e:
                self.logger.error(f"Error notifying caregivers: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Error creating wandering alert: {str(e)}")
    
    def get_safe_zone_violations(self, patient_id=None, start_time=None, end_time=None, resolved=None):
        """
        Get history of safe zone violations.
        
        Args:
            patient_id: Optional patient ID to filter by
            start_time: Optional start time (datetime)
            end_time: Optional end time (datetime)
            resolved: Optional filter by resolution status (True/False)
            
        Returns:
            list: Alerts for safe zone violations
        """
        try:
            # Build query
            query = Alert.query.filter(Alert.alert_type == 'wandering')
            
            if patient_id:
                query = query.filter(Alert.patient_id == patient_id)
            
            if start_time:
                query = query.filter(Alert.timestamp >= start_time)
            
            if end_time:
                query = query.filter(Alert.timestamp <= end_time)
            
            if resolved is not None:
                query = query.filter(Alert.is_resolved == resolved)
            
            # Get results
            alerts = query.order_by(Alert.timestamp.desc()).all()
            
            # Convert to list of dicts
            result = []
            for alert in alerts:
                result.append({
                    'id': alert.id,
                    'patient_id': alert.patient_id,
                    'message': alert.message,
                    'latitude': alert.latitude,
                    'longitude': alert.longitude,
                    'is_resolved': alert.is_resolved,
                    'timestamp': alert.timestamp.isoformat() if alert.timestamp else None
                })
            
            return result
        except Exception as e:
            self.logger.error(f"Error getting safe zone violations: {str(e)}")
            return []