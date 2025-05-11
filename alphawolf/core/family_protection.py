###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# FAMILY PROTECTION MODULE
# Specialized AI system that integrates with Aegis AI to provide
# comprehensive family protection, safety monitoring, and threat detection.
###############################################################################

import os
import logging
import json
from datetime import datetime
import time
from typing import Dict, List, Any, Optional
import uuid

logger = logging.getLogger("alphawolf.family_protection")

class FamilyProtectionSystem:
    """
    Family Protection System that works with Aegis AI to protect family members,
    particularly focusing on children's safety and cognitive care patients.
    """
    
    def __init__(self):
        """Initialize the family protection system"""
        self.logger = logging.getLogger(__name__)
        
        # Set up storage directories
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.protection_dir = os.path.join(self.data_dir, 'protection')
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.protection_dir, exist_ok=True)
        
        # Load safety zones
        self.safety_zones_file = os.path.join(self.protection_dir, 'safety_zones.json')
        self.safety_zones = self._load_safety_zones()
        
        # Load alert history
        self.alerts_file = os.path.join(self.protection_dir, 'alerts.json')
        self.alerts = self._load_alerts()
        
        # Configuration settings
        self.config = {
            'geofencing_enabled': True,
            'check_interval': 5,  # minutes
            'high_risk_threshold': 80,
            'medium_risk_threshold': 50,
            'notification_channels': ['mobile', 'email', 'call'],
            'aegis_integration': True
        }
        
        self.logger.info("Family Protection System initialized")
    
    def _load_safety_zones(self) -> List[Dict[str, Any]]:
        """Load safety zones from storage"""
        if os.path.exists(self.safety_zones_file):
            try:
                with open(self.safety_zones_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading safety zones: {str(e)}")
                return self._create_default_safety_zones()
        else:
            return self._create_default_safety_zones()
    
    def _create_default_safety_zones(self) -> List[Dict[str, Any]]:
        """Create a default set of safety zones"""
        default_zones = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Home',
                'type': 'safe',
                'radius': 100,  # meters
                'latitude': 40.7128,  # Default coordinates (New York City)
                'longitude': -74.0060,
                'address': '123 Home Street',
                'created_at': datetime.now().isoformat(),
                'active': True
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'School',
                'type': 'safe',
                'radius': 200,  # meters
                'latitude': 40.7135,  # Near default coordinates
                'longitude': -74.0046,
                'address': '456 School Avenue',
                'created_at': datetime.now().isoformat(),
                'active': True
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Risk Area',
                'type': 'risk',
                'radius': 300,  # meters
                'latitude': 40.7150,  # Near default coordinates
                'longitude': -74.0080,
                'address': '789 Risk Road',
                'created_at': datetime.now().isoformat(),
                'active': True
            }
        ]
        
        # Save default zones
        try:
            with open(self.safety_zones_file, 'w') as f:
                json.dump(default_zones, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving default safety zones: {str(e)}")
        
        return default_zones
    
    def _load_alerts(self) -> List[Dict[str, Any]]:
        """Load alert history from storage"""
        if os.path.exists(self.alerts_file):
            try:
                with open(self.alerts_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading alerts: {str(e)}")
                return []
        return []
    
    def _save_alerts(self) -> bool:
        """Save alert history to storage"""
        try:
            with open(self.alerts_file, 'w') as f:
                json.dump(self.alerts, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving alerts: {str(e)}")
            return False
    
    def check_location_safety(self, client_id: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Check if a location is within a safe zone or risk zone.
        
        Args:
            client_id: ID of the client to check
            latitude: Current latitude
            longitude: Current longitude
            
        Returns:
            Dictionary with safety status information
        """
        if not self.config['geofencing_enabled']:
            return {'is_safe': True, 'in_risk_zone': False, 'nearest_safe_zone': None}
        
        in_safe_zone = False
        in_risk_zone = False
        nearest_safe_zone = None
        nearest_safe_distance = float('inf')
        
        for zone in self.safety_zones:
            if not zone['active']:
                continue
                
            # Calculate distance to zone center
            from math import radians, cos, sin, asin, sqrt
            
            def haversine(lat1, lon1, lat2, lon2):
                """Calculate the great circle distance between two points in kilometers"""
                # Convert decimal degrees to radians
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                
                # Haversine formula
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                r = 6371  # Radius of earth in kilometers
                return c * r * 1000  # Convert to meters
            
            distance = haversine(latitude, longitude, zone['latitude'], zone['longitude'])
            
            # Check if within zone radius
            if distance <= zone['radius']:
                if zone['type'] == 'safe':
                    in_safe_zone = True
                    if distance < nearest_safe_distance:
                        nearest_safe_distance = distance
                        nearest_safe_zone = zone
                elif zone['type'] == 'risk':
                    in_risk_zone = True
            
            # Track nearest safe zone regardless of whether in it
            if zone['type'] == 'safe' and distance < nearest_safe_distance:
                nearest_safe_distance = distance
                nearest_safe_zone = zone
        
        # Prepare result
        result = {
            'is_safe': in_safe_zone,
            'in_risk_zone': in_risk_zone,
            'nearest_safe_zone': nearest_safe_zone,
            'nearest_safe_distance': round(nearest_safe_distance) if nearest_safe_zone else None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate alert if in risk zone
        if in_risk_zone:
            self._create_location_alert(client_id, latitude, longitude, result)
        
        return result
    
    def _create_location_alert(self, client_id: str, latitude: float, longitude: float, safety_status: Dict[str, Any]) -> None:
        """
        Create a location-based alert.
        
        Args:
            client_id: ID of the client
            latitude: Current latitude
            longitude: Current longitude
            safety_status: Safety status information
        """
        alert = {
            'id': str(uuid.uuid4()),
            'client_id': client_id,
            'alert_type': 'location',
            'severity': 'high' if safety_status['in_risk_zone'] else 'medium',
            'message': 'Client in risk zone' if safety_status['in_risk_zone'] else 'Client outside of safe zones',
            'latitude': latitude,
            'longitude': longitude,
            'safety_status': safety_status,
            'timestamp': datetime.now().isoformat(),
            'resolved': False,
            'resolution_timestamp': None,
            'resolution_notes': None
        }
        
        self.alerts.append(alert)
        self._save_alerts()
        
        # Trigger notifications
        self._send_alert_notifications(alert)
    
    def _send_alert_notifications(self, alert: Dict[str, Any]) -> None:
        """
        Send notifications for an alert.
        
        Args:
            alert: Alert information
        """
        # In a real implementation, this would send actual notifications
        notification_methods = {
            'mobile': self._send_mobile_notification,
            'email': self._send_email_notification,
            'call': self._send_automated_call
        }
        
        for channel in self.config['notification_channels']:
            if channel in notification_methods:
                notification_methods[channel](alert)
    
    def _send_mobile_notification(self, alert: Dict[str, Any]) -> None:
        """Send a mobile push notification"""
        self.logger.info(f"MOBILE NOTIFICATION: {alert['message']} for client {alert['client_id']}")
    
    def _send_email_notification(self, alert: Dict[str, Any]) -> None:
        """Send an email notification"""
        self.logger.info(f"EMAIL NOTIFICATION: {alert['message']} for client {alert['client_id']}")
    
    def _send_automated_call(self, alert: Dict[str, Any]) -> None:
        """Send an automated phone call"""
        if alert['severity'] == 'high':
            self.logger.info(f"AUTOMATED CALL: URGENT - {alert['message']} for client {alert['client_id']}")
    
    def add_safety_zone(self, name: str, zone_type: str, latitude: float, longitude: float, radius: float, address: str = "") -> Dict[str, Any]:
        """
        Add a new safety zone.
        
        Args:
            name: Name of the zone
            zone_type: Type of zone ('safe' or 'risk')
            latitude: Zone center latitude
            longitude: Zone center longitude
            radius: Zone radius in meters
            address: Optional address description
            
        Returns:
            The newly created zone
        """
        # Validate zone type
        if zone_type not in ['safe', 'risk']:
            raise ValueError("Zone type must be 'safe' or 'risk'")
        
        # Create zone
        zone = {
            'id': str(uuid.uuid4()),
            'name': name,
            'type': zone_type,
            'radius': radius,
            'latitude': latitude,
            'longitude': longitude,
            'address': address,
            'created_at': datetime.now().isoformat(),
            'active': True
        }
        
        # Add to zones
        self.safety_zones.append(zone)
        
        # Save zones
        try:
            with open(self.safety_zones_file, 'w') as f:
                json.dump(self.safety_zones, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving safety zones: {str(e)}")
        
        return zone
    
    def resolve_alert(self, alert_id: str, resolution_notes: str = "") -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: ID of the alert to resolve
            resolution_notes: Optional notes on resolution
            
        Returns:
            Success status
        """
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['resolved'] = True
                alert['resolution_timestamp'] = datetime.now().isoformat()
                alert['resolution_notes'] = resolution_notes
                self._save_alerts()
                return True
        
        return False
    
    def get_recent_alerts(self, client_id: Optional[str] = None, limit: int = 10, include_resolved: bool = False) -> List[Dict[str, Any]]:
        """
        Get recent alerts.
        
        Args:
            client_id: Optional client ID to filter by
            limit: Maximum number of alerts to return
            include_resolved: Whether to include resolved alerts
            
        Returns:
            List of alerts
        """
        filtered_alerts = self.alerts
        
        # Filter by client if specified
        if client_id:
            filtered_alerts = [a for a in filtered_alerts if a['client_id'] == client_id]
        
        # Filter by resolution status if needed
        if not include_resolved:
            filtered_alerts = [a for a in filtered_alerts if not a['resolved']]
        
        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda a: a['timestamp'], reverse=True)
        
        # Limit number of results
        return filtered_alerts[:limit]
    
    def integrate_with_aegis(self, client_id: str, risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate with Aegis AI for enhanced child protection.
        
        Args:
            client_id: ID of the client
            risk_assessment: Risk assessment data
            
        Returns:
            Enhanced protection data
        """
        if not self.config['aegis_integration']:
            return risk_assessment
        
        # In a real implementation, this would call the Aegis AI API
        # Here we simulate the integration
        
        # Enhanced risk factors for children
        child_protection_factors = [
            "online_safety",
            "stranger_danger",
            "cyberbullying",
            "explicit_content",
            "personal_information_sharing"
        ]
        
        # Add Aegis protection layer
        aegis_protection = {
            'enabled': True,
            'protection_level': 'high',
            'monitored_factors': child_protection_factors,
            'last_scan': datetime.now().isoformat(),
            'recommendations': [
                "Enable parental controls on all devices",
                "Review online communication regularly",
                "Discuss online safety with family members",
                "Set clear boundaries for internet usage"
            ]
        }
        
        # Combine with original assessment
        enhanced_assessment = risk_assessment.copy()
        enhanced_assessment['aegis_protection'] = aegis_protection
        
        return enhanced_assessment

# For standalone testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    protection_system = FamilyProtectionSystem()
    
    # Test location safety check
    safety = protection_system.check_location_safety("test-client", 40.7128, -74.0060)
    print(json.dumps(safety, indent=2))