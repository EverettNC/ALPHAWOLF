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
from datetime import datetime, timedelta
from geopy.distance import geodesic

logger = logging.getLogger(__name__)

class WanderingPrevention:
    """Service for detecting wandering behavior and preventing unsafe movement."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.location_history = {}  # Store location history by patient ID
        self.alert_cooldowns = {}  # Prevent alert spam by enforcing cooldowns
        self.cooldown_period = timedelta(minutes=15)  # Minimum time between alerts
        self.logger.info("Wandering prevention service initialized")
    
    def check_wandering(self, patient, safe_zones):
        """
        Check if a patient is wandering based on location and safe zones.
        
        Args:
            patient: Patient object with location data
            safe_zones: List of SafeZone objects
            
        Returns:
            bool: True if wandering detected, False otherwise
        """
        try:
            # If no location data, can't detect wandering
            if not patient.last_latitude or not patient.last_longitude:
                return False
                
            patient_id = patient.id
            current_location = (patient.last_latitude, patient.last_longitude)
            
            # Check if in safe zone
            in_safe_zone = self._is_in_safe_zones(current_location, safe_zones)
            
            # If in safe zone, not wandering
            if in_safe_zone:
                return False
            
            # Check cooldown to prevent alert spam
            if self._is_in_cooldown(patient_id):
                return False
                
            # Update location history
            self._update_location_history(patient_id, current_location)
            
            # Mark alert cooldown
            self._set_alert_cooldown(patient_id)
            
            # Patient is outside safe zones, consider this wandering
            self.logger.warning(f"Wandering detected for patient {patient_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking wandering: {str(e)}")
            return False
    
    def _is_in_safe_zones(self, location, safe_zones):
        """Check if a location is within any safe zone."""
        try:
            for zone in safe_zones:
                zone_center = (zone.latitude, zone.longitude)
                distance = geodesic(location, zone_center).meters
                
                if distance <= zone.radius:
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking safe zones: {str(e)}")
            return False
    
    def _update_location_history(self, patient_id, location):
        """Update location history for a patient."""
        if patient_id not in self.location_history:
            self.location_history[patient_id] = []
            
        # Add new location with timestamp
        self.location_history[patient_id].append({
            'location': location,
            'timestamp': datetime.utcnow()
        })
        
        # Keep only last 20 locations
        if len(self.location_history[patient_id]) > 20:
            self.location_history[patient_id].pop(0)
    
    def _is_in_cooldown(self, patient_id):
        """Check if patient is in alert cooldown period."""
        if patient_id in self.alert_cooldowns:
            cooldown_time = self.alert_cooldowns[patient_id]
            return datetime.utcnow() < cooldown_time
        return False
    
    def _set_alert_cooldown(self, patient_id):
        """Set alert cooldown for a patient."""
        self.alert_cooldowns[patient_id] = datetime.utcnow() + self.cooldown_period
    
    def get_safety_status(self, patient, safe_zones):
        """
        Get comprehensive safety status for a patient.
        
        Args:
            patient: Patient object with location data
            safe_zones: List of SafeZone objects
            
        Returns:
            dict: Safety status data
        """
        try:
            if not patient.last_latitude or not patient.last_longitude:
                return {
                    'status': 'unknown',
                    'message': 'No location data available',
                    'distance_to_zones': [],
                    'last_update': None
                }
                
            current_location = (patient.last_latitude, patient.last_longitude)
            
            # Check if in safe zone
            in_safe_zone = False
            closest_zone = None
            closest_distance = float('inf')
            distances = []
            
            for zone in safe_zones:
                zone_center = (zone.latitude, zone.longitude)
                distance = geodesic(current_location, zone_center).meters
                
                distances.append({
                    'zone_id': zone.id,
                    'zone_name': zone.name,
                    'distance': distance,
                    'inside': distance <= zone.radius
                })
                
                if distance <= zone.radius:
                    in_safe_zone = True
                
                if distance < closest_distance:
                    closest_distance = distance
                    closest_zone = zone
            
            # Sort distances from closest to furthest
            distances.sort(key=lambda x: x['distance'])
            
            # Determine status
            if in_safe_zone:
                status = 'safe'
                message = f"Within safe zone: {closest_zone.name}"
            else:
                # Check if approaching a safe zone
                if self._is_approaching_safe_zone(patient.id, closest_zone):
                    status = 'approaching'
                    message = f"Moving toward safe zone: {closest_zone.name}"
                else:
                    status = 'wandering'
                    message = f"Outside of all safe zones. Nearest: {closest_zone.name} ({int(closest_distance)}m away)"
            
            return {
                'status': status,
                'message': message,
                'distance_to_zones': distances,
                'last_update': patient.last_location_update.isoformat() if patient.last_location_update else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting safety status: {str(e)}")
            return {
                'status': 'error',
                'message': f"Error determining safety status: {str(e)}",
                'distance_to_zones': [],
                'last_update': None
            }
    
    def _is_approaching_safe_zone(self, patient_id, target_zone):
        """
        Determine if a patient is moving toward a safe zone based on recent movement.
        
        Args:
            patient_id: ID of the patient
            target_zone: SafeZone object to check if approaching
            
        Returns:
            bool: True if approaching, False otherwise
        """
        if patient_id not in self.location_history or len(self.location_history[patient_id]) < 3:
            return False
            
        try:
            # Get recent locations (newest first)
            recent_locations = list(reversed(self.location_history[patient_id][-3:]))
            
            # Calculate distances to target zone
            zone_center = (target_zone.latitude, target_zone.longitude)
            distances = []
            
            for entry in recent_locations:
                location = entry['location']
                distance = geodesic(location, zone_center).meters
                distances.append(distance)
            
            # If distances are decreasing, patient is approaching
            return distances[0] < distances[1] < distances[2]
            
        except Exception as e:
            self.logger.error(f"Error checking if approaching safe zone: {str(e)}")
            return False
