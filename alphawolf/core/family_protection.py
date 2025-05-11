###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# FAMILY PROTECTION SYSTEM
# Specialized AI system that integrates with Aegis AI to provide comprehensive
# family protection, safety monitoring, and threat detection.
###############################################################################

import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class FamilyProtectionSystem:
    """
    Family Protection System - Core module for safety monitoring and alerts
    
    Manages location tracking, safety zones, risk assessment, and integration with
    external systems like Aegis AI for comprehensive family protection.
    """
    
    def __init__(self):
        """Initialize the Family Protection System."""
        self.safe_zones = {}
        self.client_locations = {}
        self.alert_history = {}
        
        # Load safety zones from database or file
        self._load_safe_zones()
        
        logger.info("Family Protection System initialized")
    
    def _load_safe_zones(self):
        """Load safety zones from database or configuration file."""
        try:
            # In production, this would load from a database
            # For now, we'll use a local file if available
            zones_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     'data', 'safety_zones.json')
            
            if os.path.exists(zones_file):
                with open(zones_file, 'r') as f:
                    zones_data = json.load(f)
                    
                for client_id, zones in zones_data.items():
                    self.safe_zones[client_id] = zones
                
                logger.info(f"Loaded {len(self.safe_zones)} client safety zones")
            else:
                logger.warning("No safety zones file found. Using empty configuration.")
        except Exception as e:
            logger.error(f"Error loading safety zones: {str(e)}")
            # Proceed with empty configuration
    
    def check_location_safety(self, client_id: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Check if a location is within defined safety zones for a client.
        
        Args:
            client_id: The client identifier
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Dict with safety status and information
        """
        # Update client location record
        self._update_client_location(client_id, latitude, longitude)
        
        # Get client safety zones
        client_zones = self.safe_zones.get(client_id, [])
        
        # If no zones defined, location is considered uncertain
        if not client_zones:
            return {
                'is_safe': None,  # Uncertain
                'zone_name': None,
                'distance_to_nearest': None,
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
        
        # Check each zone
        in_safe_zone = False
        nearest_zone = None
        nearest_distance = float('inf')
        nearest_zone_name = None
        
        for zone in client_zones:
            # Calculate distance to zone center
            zone_lat = zone.get('latitude', 0)
            zone_long = zone.get('longitude', 0)
            zone_radius = zone.get('radius', 100)  # Default 100m radius
            
            distance = self._calculate_distance(latitude, longitude, zone_lat, zone_long)
            
            # Check if in this zone
            if distance <= zone_radius:
                in_safe_zone = True
                nearest_zone = zone
                nearest_distance = distance
                nearest_zone_name = zone.get('name', 'Unknown Zone')
                break
            
            # Track nearest zone
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_zone = zone
                nearest_zone_name = zone.get('name', 'Unknown Zone')
        
        # Prepare result
        result = {
            'is_safe': in_safe_zone,
            'zone_name': nearest_zone_name if in_safe_zone else None,
            'distance_to_nearest': nearest_distance,
            'nearest_zone': nearest_zone_name,
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
        
        # Generate alert if needed
        if not in_safe_zone and nearest_distance < 10000:  # Only alert if within 10km
            self._generate_location_alert(client_id, result)
        
        return result
    
    def _update_client_location(self, client_id: str, latitude: float, longitude: float):
        """
        Update stored client location.
        
        Args:
            client_id: The client identifier
            latitude: Location latitude
            longitude: Location longitude
        """
        current_time = datetime.utcnow()
        
        # Create or update location record
        self.client_locations[client_id] = {
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': current_time.isoformat() + "Z",
            'unix_time': int(time.time())
        }
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates in meters.
        Uses the Haversine formula for great-circle distance.
        
        Args:
            lat1: Latitude of point 1
            lon1: Longitude of point 1
            lat2: Latitude of point 2
            lon2: Longitude of point 2
            
        Returns:
            Distance in meters
        """
        import math
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Earth radius in meters
        earth_radius = 6371000
        
        # Difference in coordinates
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = earth_radius * c
        
        return distance
    
    def _generate_location_alert(self, client_id: str, location_data: Dict[str, Any]):
        """
        Generate an alert for a client being outside safe zones.
        
        Args:
            client_id: The client identifier
            location_data: Location checking result
        """
        # Check if we've recently alerted for this client (prevent spam)
        last_alert_time = self.alert_history.get(client_id, {}).get('last_location_alert', 0)
        current_time = int(time.time())
        
        # Only alert if no recent alert in last 15 minutes
        if current_time - last_alert_time < 900:  # 15 minutes = 900 seconds
            return
        
        # Create alert
        alert = {
            'client_id': client_id,
            'alert_type': 'location_safety',
            'severity': 'medium',
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'message': f"Client is outside of designated safe zones. Nearest zone: {location_data['nearest_zone']} ({location_data['distance_to_nearest']:.0f}m away).",
            'location': {
                'latitude': self.client_locations[client_id]['latitude'],
                'longitude': self.client_locations[client_id]['longitude']
            },
            'metadata': {
                'nearest_zone': location_data['nearest_zone'],
                'distance': location_data['distance_to_nearest']
            }
        }
        
        # In a production system, this would send to an alerts queue or notification system
        logger.warning(f"LOCATION ALERT: {alert['message']}")
        
        # Update alert history
        if client_id not in self.alert_history:
            self.alert_history[client_id] = {}
        
        self.alert_history[client_id]['last_location_alert'] = current_time
        
        # Return the alert for potential further processing
        return alert
    
    def integrate_with_aegis(self, client_id: str, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate with Aegis AI for enhanced risk assessment.
        
        Args:
            client_id: The client identifier
            assessment_data: Current risk assessment data
            
        Returns:
            Enhanced assessment from Aegis AI
        """
        try:
            # In production, this would call the Aegis AI API
            # For now, we'll simulate the integration
            
            # Check if AEGIS_API_KEY is available
            if not os.environ.get('AEGIS_API_KEY'):
                logger.warning("No Aegis API key available. Using simulated response.")
                return self._simulate_aegis_response(client_id, assessment_data)
            
            # Here would be the actual API call to Aegis
            # Using a placeholder for now
            logger.info(f"Integrating with Aegis AI for client {client_id}")
            
            # Simulate processing time
            time.sleep(0.1)
            
            return self._simulate_aegis_response(client_id, assessment_data)
            
        except Exception as e:
            logger.error(f"Error integrating with Aegis AI: {str(e)}")
            return {
                'error': f"Failed to integrate with Aegis: {str(e)}",
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
    
    def _simulate_aegis_response(self, client_id: str, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate Aegis AI response for testing.
        
        Args:
            client_id: The client identifier
            assessment_data: Current risk assessment data
            
        Returns:
            Simulated Aegis AI response
        """
        risk_score = assessment_data.get('risk_score', 0)
        risk_factors = assessment_data.get('risk_factors', [])
        location_safety = assessment_data.get('location_safety', {})
        
        # Enhanced risk categorization
        risk_category = 'low'
        if risk_score >= 85:
            risk_category = 'critical'
        elif risk_score >= 70:
            risk_category = 'high'
        elif risk_score >= 50:
            risk_category = 'medium'
        
        # Generate recommendations based on risk factors
        recommendations = []
        
        if 'wandering' in [f.get('category') for f in risk_factors]:
            recommendations.append("Activate enhanced location monitoring")
            recommendations.append("Ensure client has ID and contact information")
            recommendations.append("Consider real-time location sharing with caregivers")
        
        if 'confusion' in [f.get('category') for f in risk_factors]:
            recommendations.append("Provide clear, simple instructions")
            recommendations.append("Minimize environmental distractions")
            recommendations.append("Consider using visual cues and reminders")
        
        if 'distress' in [f.get('category') for f in risk_factors]:
            recommendations.append("Use calming techniques and reassurance")
            recommendations.append("Maintain a calm environment")
            recommendations.append("Consider contacting a trusted caregiver")
        
        if 'medical_emergency' in [f.get('category') for f in risk_factors]:
            recommendations.append("**Contact emergency services immediately**")
            recommendations.append("Have medical information ready")
            recommendations.append("Stay with the client until help arrives")
        
        # Determine if alert should be generated
        generate_alert = risk_category in ['high', 'critical']
        
        # Location-based recommendations
        if location_safety and not location_safety.get('is_safe'):
            recommendations.append("Monitor location closely as client is outside safe zones")
            if location_safety.get('distance_to_nearest', 0) > 1000:  # Over 1km away
                recommendations.append("Consider activating return to safe zone protocol")
                generate_alert = True
        
        # Generate response
        response = {
            'client_id': client_id,
            'aegis_assessment': {
                'risk_category': risk_category,
                'confidence': min(risk_score / 100 + 0.15, 0.99),  # Adjust confidence based on risk score
                'recommendations': recommendations,
                'generate_alert': generate_alert,
                'alert_recipients': ['primary_caregiver', 'family'],
                'alert_channels': ['app', 'sms', 'email'] if risk_category == 'critical' else ['app'],
                'assessment_id': f"aegis-{int(time.time())}-{hash(client_id) % 10000:04d}",
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
        }
        
        # If alert should be generated, add it to the response
        if generate_alert:
            alert_text = f"ALERT: {risk_category.upper()} risk detected for client {client_id}."
            if risk_factors:
                top_factor = risk_factors[0].get('category', '').replace('_', ' ').title()
                alert_text += f" Primary concern: {top_factor}."
            
            response['aegis_assessment']['alert'] = {
                'text': alert_text,
                'severity': 'high' if risk_category == 'critical' else 'medium',
                'actions_required': recommendations[:3]  # Top 3 recommendations
            }
            
            logger.warning(f"AEGIS ALERT: {alert_text}")
        
        return response
    
    def add_safe_zone(self, client_id: str, zone_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new safety zone for a client.
        
        Args:
            client_id: The client identifier
            zone_data: Safety zone definition
            
        Returns:
            Result of the operation
        """
        # Validate required fields
        required_fields = ['name', 'latitude', 'longitude', 'radius']
        for field in required_fields:
            if field not in zone_data:
                return {
                    'success': False,
                    'error': f"Missing required field: {field}",
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
        
        # Ensure client exists in safe zones
        if client_id not in self.safe_zones:
            self.safe_zones[client_id] = []
        
        # Add zone with metadata
        zone = {
            'id': zone_data.get('id', f"zone-{int(time.time())}-{len(self.safe_zones[client_id]):04d}"),
            'name': zone_data['name'],
            'latitude': float(zone_data['latitude']),
            'longitude': float(zone_data['longitude']),
            'radius': float(zone_data['radius']),
            'created_at': datetime.utcnow().isoformat() + "Z"
        }
        
        # Add optional fields
        for field in ['description', 'type', 'color']:
            if field in zone_data:
                zone[field] = zone_data[field]
        
        # Add to client's zones
        self.safe_zones[client_id].append(zone)
        
        # Save zones (in production, would save to database)
        self._save_safe_zones()
        
        logger.info(f"Added safe zone '{zone['name']}' for client {client_id}")
        
        return {
            'success': True,
            'zone_id': zone['id'],
            'message': f"Safety zone '{zone['name']}' added successfully",
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
    
    def _save_safe_zones(self):
        """Save safety zones to database or file."""
        try:
            # In production, this would save to a database
            # For now, we'll save to a local file
            zones_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     'data', 'safety_zones.json')
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(zones_file), exist_ok=True)
            
            with open(zones_file, 'w') as f:
                json.dump(self.safe_zones, f, indent=2)
            
            logger.info(f"Saved {len(self.safe_zones)} client safety zones")
        except Exception as e:
            logger.error(f"Error saving safety zones: {str(e)}")
    
    def get_client_safe_zones(self, client_id: str) -> List[Dict[str, Any]]:
        """
        Get all safety zones for a client.
        
        Args:
            client_id: The client identifier
            
        Returns:
            List of safety zones
        """
        return self.safe_zones.get(client_id, [])