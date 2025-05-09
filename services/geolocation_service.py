import logging
import json
from geopy.distance import geodesic
from datetime import datetime

logger = logging.getLogger(__name__)

class GeolocationService:
    """Service for processing geolocation data and detecting wandering behavior."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.location_history = {}  # Store recent locations by patient_id
        self.safe_zones = []  # List of safe zones
        self.mqtt_client = None  # Would be initialized for real-time alerts
        
        self.logger.info("Geolocation service initialized")
    
    def update_location(self, patient_id, latitude, longitude, timestamp=None):
        """
        Update a patient's location and store in history.
        
        Args:
            patient_id: ID of the patient
            latitude: Current latitude
            longitude: Current longitude
            timestamp: Optional timestamp, defaults to current time
        
        Returns:
            bool: Success of update
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        location = {
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': timestamp
        }
        
        # Initialize history for new patients
        if patient_id not in self.location_history:
            self.location_history[patient_id] = []
        
        # Add to history, keeping only last 100 points
        self.location_history[patient_id].append(location)
        if len(self.location_history[patient_id]) > 100:
            self.location_history[patient_id].pop(0)
            
        self.logger.debug(f"Updated location for patient {patient_id}: {latitude}, {longitude}")
        return True
    
    def is_in_safe_zone(self, latitude, longitude, safe_zones=None):
        """
        Check if a location is within any safe zone.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            safe_zones: Optional list of safe zones, uses stored zones if None
        
        Returns:
            tuple: (bool indicating if in safe zone, name of zone if in one)
        """
        if safe_zones is None:
            safe_zones = self.safe_zones
            
        if not safe_zones:
            self.logger.warning("No safe zones defined")
            return False, None
            
        point = (latitude, longitude)
        
        for zone in safe_zones:
            zone_center = (zone['latitude'], zone['longitude'])
            distance = geodesic(point, zone_center).meters
            
            if distance <= zone['radius']:
                self.logger.info(f"Location {point} is within safe zone '{zone['name']}'")
                return True, zone['name']
                
        self.logger.info(f"Location {point} is outside all safe zones")
        return False, None
    
    def load_safe_zones(self, zones_data):
        """
        Load safe zones from database or configuration.
        
        Args:
            zones_data: List of safe zone dictionaries with name, latitude, longitude, radius
        """
        self.safe_zones = zones_data
        self.logger.info(f"Loaded {len(self.safe_zones)} safe zones")
    
    def detect_wandering(self, patient_id, current_location, safe_zones=None):
        """
        Detect potential wandering behavior based on location and safe zones.
        
        Args:
            patient_id: ID of the patient
            current_location: Dict with latitude and longitude
            safe_zones: Optional list of safe zones
            
        Returns:
            dict: Wandering assessment with status and details
        """
        latitude = current_location['latitude']
        longitude = current_location['longitude']
        
        # Check if patient is in a safe zone
        in_safe_zone, zone_name = self.is_in_safe_zone(latitude, longitude, safe_zones)
        
        if in_safe_zone:
            return {
                'wandering': False,
                'zone': zone_name,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # If not in safe zone, check movement patterns
        # Get recent history
        if patient_id in self.location_history and len(self.location_history[patient_id]) > 5:
            recent_points = self.location_history[patient_id][-5:]
            
            # Check for erratic movement patterns
            distances = []
            for i in range(1, len(recent_points)):
                p1 = (recent_points[i-1]['latitude'], recent_points[i-1]['longitude'])
                p2 = (recent_points[i]['latitude'], recent_points[i]['longitude'])
                distances.append(geodesic(p1, p2).meters)
            
            # Calculate average and variance of distances
            avg_distance = sum(distances) / len(distances)
            variance = sum((d - avg_distance) ** 2 for d in distances) / len(distances)
            
            # Identify potential wandering
            if avg_distance > 50 and variance > 100:  # Thresholds can be adjusted
                return {
                    'wandering': True,
                    'zone': None,
                    'reason': 'erratic_movement',
                    'details': {
                        'avg_distance': avg_distance,
                        'variance': variance
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        # Default case: outside safe zone but not showing erratic patterns yet
        return {
            'wandering': True,
            'zone': None,
            'reason': 'outside_safe_zone',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def calculate_distance_from_zones(self, latitude, longitude, safe_zones=None):
        """
        Calculate distances from a point to all safe zones.
        
        Args:
            latitude: Point latitude
            longitude: Point longitude
            safe_zones: Optional list of safe zones
            
        Returns:
            list: Distances to each safe zone in meters
        """
        if safe_zones is None:
            safe_zones = self.safe_zones
            
        if not safe_zones:
            return []
            
        point = (latitude, longitude)
        distances = []
        
        for zone in safe_zones:
            zone_center = (zone['latitude'], zone['longitude'])
            distance = geodesic(point, zone_center).meters
            distances.append({
                'zone_name': zone['name'],
                'distance': distance,
                'inside': distance <= zone['radius']
            })
            
        return distances
