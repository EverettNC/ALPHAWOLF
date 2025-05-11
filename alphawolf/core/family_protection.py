"""
AlphaWolf Family Protection System
Part of The Christman AI Project - LumaCognify AI

This module provides family protection features for AlphaWolf, focusing on
safety monitoring, geofencing, and alert generation for dementia and Alzheimer's patients.

"HOW CAN I HELP YOU LOVE YOURSELF MORE"
"""

import os
import json
import logging
import datetime
import hashlib
import re
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple, Union
from urllib.parse import urlparse

# Import local modules
try:
    from .utils import (
        calculate_distance,
        is_inside_polygon,
        generate_unique_id,
        validate_coordinates,
        format_timestamp
    )
except ImportError:
    # When running as Lambda function
    from utils import (
        calculate_distance,
        is_inside_polygon,
        generate_unique_id,
        validate_coordinates,
        format_timestamp
    )

# Configure logging
logger = logging.getLogger(__name__)
log_level = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))

# Constants
DEFAULT_CONFIG = {
    "high_risk_threshold": float(os.environ.get("HIGH_RISK_THRESHOLD", "0.7")),
    "medium_risk_threshold": float(os.environ.get("MEDIUM_RISK_THRESHOLD", "0.4")),
    "alert_notification_email": os.environ.get("ALERT_NOTIFICATION_EMAIL", "alerts@example.com"),
    "max_cache_age_days": int(os.environ.get("MAX_CACHE_AGE_DAYS", "7")),
    "safe_speed_threshold_kph": 60.0,  # Maximum safe speed in km/h
    "unsafe_words": [
        "lost", "confused", "help", "don't know", "where am i",
        "scared", "afraid", "alone", "hurt", "pain", "fallen",
        "emergency", "hospital", "police", "forgot", "not sure", "stranger"
    ]
}

# Initialize optional services
try:
    import boto3
    # Initialize AWS services if running in AWS Lambda
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        sns_client = boto3.client('sns')
        sqs_client = boto3.client('sqs')
        dynamodb = boto3.resource('dynamodb')
        locations_table = dynamodb.Table(os.environ.get("LOCATIONS_TABLE", "alphawolf-locations"))
except ImportError:
    # If running outside AWS or boto3 not available
    sns_client = None
    sqs_client = None
    dynamodb = None
    locations_table = None

# Risk analysis integration
try:
    from .risk_model import RiskAnalyzer
    risk_analyzer = RiskAnalyzer()
except ImportError:
    # Simple fallback risk analyzer
    class RiskAnalyzer:
        def analyze_text(self, text, context=None):
            # Simple keyword-based risk detection as fallback
            risk_level = 0.0
            unsafe_words = DEFAULT_CONFIG["unsafe_words"]
            
            # Check for unsafe words
            text_lower = text.lower()
            for word in unsafe_words:
                if word.lower() in text_lower:
                    risk_level += 0.2
                    risk_level = min(risk_level, 0.9)  # Cap at 0.9
                    
            # Return result
            return {
                "risk_score": risk_level,
                "risk_level": "high" if risk_level >= DEFAULT_CONFIG["high_risk_threshold"] else 
                              "medium" if risk_level >= DEFAULT_CONFIG["medium_risk_threshold"] else "low",
                "unsafe_matches": [word for word in unsafe_words if word.lower() in text_lower],
                "analysis_timestamp": datetime.datetime.utcnow().isoformat()
            }
    
    risk_analyzer = RiskAnalyzer()

def analyze_text(text, context=None):
    """Helper function to analyze text with the risk analyzer"""
    return risk_analyzer.analyze_text(text, context)


class FamilyProtectionSystem:
    """
    Main class for the Family Protection System
    Provides safety monitoring and alerting capabilities
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Family Protection System
        
        Parameters:
        - config: Optional configuration dictionary
        """
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        
        # Generate a unique instance ID for logging
        instance_hash = hashlib.md5(str(datetime.datetime.utcnow().timestamp()).encode()).hexdigest()[:8]
        self.instance_id = f"family_protection_{instance_hash}"
        
        logger.info(f"FamilyProtectionSystem initialized with ID {self.instance_id}")
        
    def check_location_safety(self, 
                             latitude: float, 
                             longitude: float, 
                             safety_zones: List[Dict[str, Any]], 
                             user_id: str,
                             timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if a location is within defined safety zones
        
        Parameters:
        - latitude: The current latitude
        - longitude: The current longitude
        - safety_zones: List of safety zone definitions
        - user_id: Identifier of the user being monitored
        - timestamp: Optional timestamp of the location update
        
        Returns:
        - Safety assessment result
        """
        # Validate coordinates
        if not validate_coordinates(latitude, longitude):
            return {
                "is_safe": False,
                "error": "Invalid coordinates",
                "user_id": user_id,
                "timestamp": format_timestamp(timestamp or datetime.datetime.utcnow())
            }
            
        # Check if location is within any safety zone
        is_safe = False
        closest_zone = None
        closest_distance = float('inf')
        closest_zone_name = "Unknown"
        
        for zone in safety_zones:
            # Get zone center point or polygon
            if "center" in zone and "radius" in zone:
                # Circular zone
                center_lat = zone["center"]["latitude"]
                center_lon = zone["center"]["longitude"]
                radius = zone["radius"]
                
                # Calculate distance to center
                distance = calculate_distance(latitude, longitude, center_lat, center_lon)
                
                # Check if within radius
                if distance <= radius:
                    is_safe = True
                    closest_zone = zone
                    closest_distance = distance
                    closest_zone_name = zone.get("name", "Unnamed Safety Zone")
                    break
                elif distance < closest_distance:
                    closest_distance = distance
                    closest_zone = zone
                    closest_zone_name = zone.get("name", "Unnamed Safety Zone")
            elif "polygon" in zone:
                # Polygon zone
                polygon = zone["polygon"]
                
                # Check if inside polygon
                if is_inside_polygon(latitude, longitude, polygon):
                    is_safe = True
                    closest_zone = zone
                    closest_distance = 0  # Inside polygon
                    closest_zone_name = zone.get("name", "Unnamed Safety Zone")
                    break
                else:
                    # Find minimum distance to polygon
                    min_distance = float('inf')
                    for i in range(len(polygon)):
                        p1 = polygon[i]
                        p2 = polygon[(i + 1) % len(polygon)]
                        d = self._distance_to_segment(latitude, longitude, p1[0], p1[1], p2[0], p2[1])
                        min_distance = min(min_distance, d)
                    
                    if min_distance < closest_distance:
                        closest_distance = min_distance
                        closest_zone = zone
                        closest_zone_name = zone.get("name", "Unnamed Safety Zone")
        
        # Store location in database if available
        if locations_table:
            try:
                location_item = {
                    "user_id": user_id,
                    "timestamp": timestamp or datetime.datetime.utcnow().isoformat(),
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                    "is_safe": is_safe,
                    "closest_zone_name": closest_zone_name,
                    "distance_to_safety": closest_distance if not is_safe else 0,
                    "ttl": int(time.time() + 86400 * 30)  # 30 days retention
                }
                locations_table.put_item(Item=location_item)
            except Exception as e:
                logger.error(f"Error storing location: {e}")
        
        # Create safety assessment result
        result = {
            "is_safe": is_safe,
            "user_id": user_id,
            "timestamp": format_timestamp(timestamp or datetime.datetime.utcnow()),
            "latitude": float(latitude),
            "longitude": float(longitude),
            "assessment": {
                "closest_zone_name": closest_zone_name,
                "distance_to_safety": round(closest_distance, 2) if not is_safe else 0,
                "safety_status": "within safety zone" if is_safe else "outside safety zone"
            }
        }
        
        # Add alert details if not safe
        if not is_safe:
            result["alert"] = {
                "severity": "medium",
                "message": f"User {user_id} is outside all safety zones. Closest zone: {closest_zone_name} ({closest_distance:.2f}m away)",
                "alert_id": generate_unique_id("loc_alert"),
                "alert_timestamp": datetime.datetime.utcnow().isoformat()
            }
            
        return result
    
    def detect_unusual_movement(self, 
                               current_location: Dict[str, float], 
                               previous_locations: List[Dict[str, Any]],
                               user_id: str) -> Dict[str, Any]:
        """
        Detect unusual movement patterns that might indicate wandering or travel
        
        Parameters:
        - current_location: The current location with latitude, longitude, and timestamp
        - previous_locations: List of previous locations with timestamps
        - user_id: Identifier of the user being monitored
        
        Returns:
        - Movement assessment result
        """
        # Validate current location
        if not validate_coordinates(current_location.get("latitude"), current_location.get("longitude")):
            return {
                "is_unusual": False,
                "error": "Invalid coordinates in current location",
                "user_id": user_id,
                "timestamp": format_timestamp(datetime.datetime.utcnow())
            }
            
        # Need at least one previous location for comparison
        if not previous_locations:
            return {
                "is_unusual": False,
                "user_id": user_id,
                "timestamp": format_timestamp(datetime.datetime.utcnow()),
                "note": "Insufficient location history for movement analysis"
            }
            
        # Sort locations by timestamp
        sorted_locations = sorted(previous_locations, 
                                 key=lambda loc: loc.get("timestamp", "1970-01-01T00:00:00Z"))
        
        last_location = sorted_locations[-1]
        
        # Calculate distance and time since last recorded location
        try:
            distance = calculate_distance(
                float(current_location["latitude"]), 
                float(current_location["longitude"]),
                float(last_location["latitude"]), 
                float(last_location["longitude"])
            )
            
            # Parse timestamps
            current_time = None
            last_time = None
            
            if "timestamp" in current_location:
                try:
                    current_time = datetime.datetime.fromisoformat(str(current_location["timestamp"]).replace('Z', '+00:00'))
                except ValueError:
                    current_time = datetime.datetime.utcnow()
            else:
                current_time = datetime.datetime.utcnow()
                
            if "timestamp" in last_location:
                try:
                    last_time = datetime.datetime.fromisoformat(str(last_location["timestamp"]).replace('Z', '+00:00'))
                except ValueError:
                    # Default to 10 minutes ago if invalid
                    last_time = current_time - datetime.timedelta(minutes=10)
            else:
                # Default to 10 minutes ago if missing
                last_time = current_time - datetime.timedelta(minutes=10)
                
            # Calculate time difference in seconds
            time_diff_seconds = (current_time - last_time).total_seconds()
            
            # Avoid division by zero
            if time_diff_seconds < 1:
                time_diff_seconds = 1
                
            # Calculate speed in m/s and convert to km/h
            speed_mps = distance / time_diff_seconds
            speed_kph = speed_mps * 3.6
            
            # Check if speed exceeds threshold (unusual for someone with dementia to move so fast)
            safe_speed_threshold_kph = self.config["safe_speed_threshold_kph"]
            is_unusual_speed = speed_kph > safe_speed_threshold_kph
            
            # Check for wandering pattern (repeatedly visiting the same area)
            recent_locations = sorted_locations[-10:]  # Last 10 locations
            visited_areas = set()
            for loc in recent_locations:
                # Create a grid-based area identifier (1km grid)
                area_id = f"{int(float(loc['latitude']) * 100) / 100},{int(float(loc['longitude']) * 100) / 100}"
                visited_areas.add(area_id)
                
            potential_wandering = len(visited_areas) < 3 and len(recent_locations) >= 5
            
            # Create assessment result
            result = {
                "is_unusual": is_unusual_speed or potential_wandering,
                "user_id": user_id,
                "timestamp": format_timestamp(current_time),
                "assessment": {
                    "distance_from_last_location": round(distance, 2),
                    "time_since_last_location": round(time_diff_seconds, 2),
                    "estimated_speed_kph": round(speed_kph, 2),
                    "unusual_speed": is_unusual_speed,
                    "potential_wandering": potential_wandering
                }
            }
            
            # Add alert if movement is unusual
            if is_unusual_speed:
                result["alert"] = {
                    "severity": "high" if speed_kph > safe_speed_threshold_kph * 1.5 else "medium",
                    "message": f"User {user_id} is moving at {speed_kph:.2f} km/h, which exceeds the safe threshold of {safe_speed_threshold_kph} km/h",
                    "alert_id": generate_unique_id("mov_alert"),
                    "alert_timestamp": datetime.datetime.utcnow().isoformat()
                }
            elif potential_wandering:
                result["alert"] = {
                    "severity": "medium",
                    "message": f"User {user_id} shows potential wandering pattern, visiting {len(visited_areas)} distinct areas in the last {len(recent_locations)} location updates",
                    "alert_id": generate_unique_id("wan_alert"),
                    "alert_timestamp": datetime.datetime.utcnow().isoformat()
                }
                
            return result
            
        except Exception as e:
            logger.error(f"Error calculating movement assessment: {e}")
            return {
                "is_unusual": False,
                "error": f"Error in movement analysis: {str(e)}",
                "user_id": user_id,
                "timestamp": format_timestamp(datetime.datetime.utcnow())
            }
    
    def analyze_communication(self, 
                             message: str, 
                             user_id: str,
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze communication for signs of distress or disorientation
        
        Parameters:
        - message: The message text to analyze
        - user_id: Identifier of the user who sent the message
        - context: Optional context information
        
        Returns:
        - Communication analysis result
        """
        # Use risk analyzer to assess message
        risk_assessment = analyze_text(message, context)
        
        # Create assessment result
        result = {
            "user_id": user_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "message": message,
            "assessment": {
                "risk_score": risk_assessment["risk_score"],
                "risk_level": risk_assessment["risk_level"],
                "unsafe_matches": risk_assessment.get("unsafe_matches", [])
            }
        }
        
        # Add alert for medium and high risk messages
        if risk_assessment["risk_level"] in ["medium", "high"]:
            result["alert"] = {
                "severity": risk_assessment["risk_level"],
                "message": f"User {user_id} sent a message with {risk_assessment['risk_level']} risk level: '{message[:100]}...' if len(message) > 100 else message",
                "alert_id": generate_unique_id("msg_alert"),
                "alert_timestamp": datetime.datetime.utcnow().isoformat()
            }
            
        return result
    
    def generate_safety_report(self, 
                              user_id: str,
                              location_history: List[Dict[str, Any]],
                              safety_zones: List[Dict[str, Any]],
                              communication_history: List[Dict[str, Any]],
                              timeframe_hours: int = 24) -> Dict[str, Any]:
        """
        Generate a comprehensive safety report for a user
        
        Parameters:
        - user_id: Identifier of the user to report on
        - location_history: List of location records
        - safety_zones: List of defined safety zones
        - communication_history: List of communication records
        - timeframe_hours: Hours of history to include in report
        
        Returns:
        - Safety report
        """
        # Calculate timeframe start
        now = datetime.datetime.utcnow()
        timeframe_start = now - datetime.timedelta(hours=timeframe_hours)
        
        # Filter by timeframe
        filtered_locations = []
        for loc in location_history:
            try:
                loc_time = datetime.datetime.fromisoformat(str(loc.get("timestamp", "")).replace('Z', '+00:00'))
                if loc_time >= timeframe_start:
                    filtered_locations.append(loc)
            except (ValueError, TypeError):
                # Skip entries with invalid timestamps
                continue
                
        filtered_communications = []
        for comm in communication_history:
            try:
                comm_time = datetime.datetime.fromisoformat(str(comm.get("timestamp", "")).replace('Z', '+00:00'))
                if comm_time >= timeframe_start:
                    filtered_communications.append(comm)
            except (ValueError, TypeError):
                # Skip entries with invalid timestamps
                continue
        
        # Calculate time in/outside safety zones
        time_in_zones = 0.0
        time_outside_zones = 0.0
        zone_visits = {}
        last_loc = None
        
        for loc in sorted(filtered_locations, key=lambda x: x.get("timestamp", "")):
            # Initialize counter for each zone
            for zone in safety_zones:
                zone_name = zone.get("name", "Unnamed Zone")
                if zone_name not in zone_visits:
                    zone_visits[zone_name] = 0.0
            
            is_inside_any_zone = False
            inside_zone_name = "Outside All Zones"
            
            # Check each zone
            for zone in safety_zones:
                zone_name = zone.get("name", "Unnamed Zone")
                
                # Check if in circular zone
                if "center" in zone and "radius" in zone:
                    center_lat = zone["center"]["latitude"]
                    center_lon = zone["center"]["longitude"]
                    radius = zone["radius"]
                    
                    distance = calculate_distance(
                        float(loc["latitude"]), 
                        float(loc["longitude"]),
                        float(center_lat), 
                        float(center_lon)
                    )
                    
                    if distance <= radius:
                        is_inside_any_zone = True
                        inside_zone_name = zone_name
                        break
                        
                # Check if in polygon zone
                elif "polygon" in zone:
                    polygon = zone["polygon"]
                    
                    if is_inside_polygon(float(loc["latitude"]), float(loc["longitude"]), polygon):
                        is_inside_any_zone = True
                        inside_zone_name = zone_name
                        break
            
            # Calculate duration since last location
            if last_loc:
                try:
                    last_time = datetime.datetime.fromisoformat(str(last_loc.get("timestamp", "")).replace('Z', '+00:00'))
                    current_time = datetime.datetime.fromisoformat(str(loc.get("timestamp", "")).replace('Z', '+00:00'))
                    
                    # Duration in hours
                    duration = (current_time - last_time).total_seconds() / 3600
                    
                    # Add to appropriate counter
                    if is_inside_any_zone:
                        time_in_zones += duration
                        zone_visits[inside_zone_name] += duration
                    else:
                        time_outside_zones += duration
                except (ValueError, TypeError):
                    # Skip if timestamps can't be parsed
                    pass
                    
            # Update last location
            last_loc = loc
        
        # Analyze alerts
        alerts = []
        for loc in filtered_locations:
            if "alert" in loc:
                alerts.append(loc["alert"])
                
        for comm in filtered_communications:
            if "alert" in comm:
                alerts.append(comm["alert"])
                
        # Count alerts by severity
        high_alerts = len([a for a in alerts if a.get("severity") == "high"])
        medium_alerts = len([a for a in alerts if a.get("severity") == "medium"])
        low_alerts = len([a for a in alerts if a.get("severity") == "low"])
        
        # Count concerning communications
        concerning_comms = len([
            c for c in filtered_communications 
            if c.get("assessment", {}).get("risk_level") in ["medium", "high"]
        ])
        
        # Calculate safety score
        safety_score = self._calculate_safety_score(
            time_in_zones,
            time_outside_zones,
            high_alerts + medium_alerts,
            concerning_comms
        )
        
        # Generate safety interpretation
        safety_interpretation = self._interpret_safety_score(safety_score)
        
        # Create report
        report = {
            "user_id": user_id,
            "report_id": generate_unique_id("report"),
            "generated_at": now.isoformat(),
            "timeframe_hours": timeframe_hours,
            "summary": {
                "safety_score": round(safety_score, 1),
                "assessment": safety_interpretation["assessment"],
                "locations_analyzed": len(filtered_locations),
                "communications_analyzed": len(filtered_communications),
                "hours_in_safety_zones": round(time_in_zones, 2),
                "hours_outside_safety_zones": round(time_outside_zones, 2),
                "safety_zone_visits": {k: round(v, 2) for k, v in zone_visits.items() if v > 0},
                "total_alerts": len(alerts),
                "high_priority_alerts": high_alerts,
                "medium_priority_alerts": medium_alerts,
                "low_priority_alerts": low_alerts,
                "concerning_communications": concerning_comms
            },
            "recommendations": safety_interpretation["recommendations"]
        }
        
        return report
    
    def _distance_to_segment(self, lat: float, lon: float, 
                            lat1: float, lon1: float, 
                            lat2: float, lon2: float) -> float:
        """
        Calculate minimum distance from point to line segment
        
        Parameters:
        - lat, lon: The point to check
        - lat1, lon1: First endpoint of the line segment
        - lat2, lon2: Second endpoint of the line segment
        
        Returns:
        - Minimum distance in meters
        """
        # Helper function to dot product
        def dot(v1, v2):
            return v1[0] * v2[0] + v1[1] * v2[1]
            
        # Helper function to get vector length
        def length(v):
            return (v[0]**2 + v[1]**2)**0.5
            
        # Helper function to normalize a vector
        def normalize(v):
            len_v = length(v)
            return [v[0] / len_v, v[1] / len_v] if len_v > 0 else [0, 0]
            
        # Convert to Cartesian coordinates for simplicity
        # This is an approximation that works for short distances
        earth_radius = 6371000  # in meters
        lat_scale = 111320  # meters per degree latitude (approximate)
        lon_scale = 111320 * abs(math.cos(math.radians(lat)))  # meters per degree longitude (approximate)
        
        px = lon * lon_scale
        py = lat * lat_scale
        p1x = lon1 * lon_scale
        p1y = lat1 * lat_scale
        p2x = lon2 * lon_scale
        p2y = lat2 * lat_scale
        
        # Calculate distance
        segment = [p2x - p1x, p2y - p1y]
        segment_len = length(segment)
        
        if segment_len == 0:
            # The segment is actually a point
            return calculate_distance(lat, lon, lat1, lon1)
            
        # Calculate normalized direction vector
        segment_norm = normalize(segment)
        
        # Calculate vector from p1 to point
        p_to_p1 = [px - p1x, py - p1y]
        
        # Calculate projection of p_to_p1 onto the normalized segment
        projection = dot(p_to_p1, segment_norm)
        
        # Calculate the closest point on the line
        if projection <= 0:
            # Closest point is p1
            return calculate_distance(lat, lon, lat1, lon1)
        elif projection >= segment_len:
            # Closest point is p2
            return calculate_distance(lat, lon, lat2, lon2)
        else:
            # Closest point is on the segment
            close_x = p1x + segment_norm[0] * projection
            close_y = p1y + segment_norm[1] * projection
            
            # Convert back to lat/lon and calculate distance
            close_lon = close_x / lon_scale
            close_lat = close_y / lat_scale
            
            return calculate_distance(lat, lon, close_lat, close_lon)
    
    def _calculate_safety_score(self, 
                               time_in_zones: float, 
                               time_outside_zones: float,
                               alert_count: int,
                               concerning_comm_count: int) -> float:
        """
        Calculate an overall safety score from 0-100
        
        Parameters:
        - time_in_zones: Hours spent in safety zones
        - time_outside_zones: Hours spent outside safety zones
        - alert_count: Number of alerts triggered
        - concerning_comm_count: Number of concerning communications
        
        Returns:
        - Safety score from 0-100
        """
        # Calculate percentage of time in safety zones
        total_time = time_in_zones + time_outside_zones
        if total_time < 0.1:  # Less than 6 minutes of data
            zone_score = 50  # Neutral score
        else:
            zone_percentage = (time_in_zones / total_time) * 100
            zone_score = min(100, zone_percentage)  # 0-100
            
        # Alert penalty (each alert reduces score)
        alert_penalty = alert_count * 10
        
        # Communication penalty
        comm_penalty = concerning_comm_count * 5
        
        # Calculate final score
        safety_score = zone_score - alert_penalty - comm_penalty
        
        # Ensure score is between 0 and 100
        return max(0, min(100, safety_score))
    
    def _interpret_safety_score(self, score: float) -> Dict[str, Any]:
        """
        Interpret a safety score
        
        Parameters:
        - score: Safety score from 0-100
        
        Returns:
        - Dictionary with assessment and recommendations
        """
        if score >= 90:
            assessment = "Excellent"
            recommendations = [
                "Continue monitoring as usual.",
                "No immediate actions needed.",
                "Schedule regular check-ins to maintain awareness."
            ]
        elif score >= 75:
            assessment = "Good"
            recommendations = [
                "Continue current safety protocols.",
                "Consider reviewing safety zones if user's routine has changed.",
                "Schedule a check-in within the next 48 hours."
            ]
        elif score >= 60:
            assessment = "Satisfactory"
            recommendations = [
                "Review recent alerts to identify patterns.",
                "Consider expanding safety zones to include frequent destinations.",
                "Increase check-in frequency to once per day.",
                "Review emergency contact information."
            ]
        elif score >= 40:
            assessment = "Concerning"
            recommendations = [
                "Immediate review of all recent alerts recommended.",
                "Consider in-person visit within 24 hours.",
                "Verify location tracking is working properly.",
                "Review medication regimen if applicable.",
                "Ensure emergency contacts are updated and aware."
            ]
        else:
            assessment = "Critical"
            recommendations = [
                "Immediate in-person check recommended.",
                "Review all recent activity for urgent issues.",
                "Consider temporary increased supervision.",
                "Consult with healthcare provider.",
                "Verify all safety systems are functioning properly.",
                "Update emergency protocols and contacts."
            ]
            
        return {
            "assessment": assessment,
            "recommendations": recommendations
        }


# Create default instance
default_system = FamilyProtectionSystem()

# Convenience functions
def check_location_safety(latitude, longitude, safety_zones, user_id, timestamp=None):
    """Convenience function to check location safety using default system"""
    return default_system.check_location_safety(latitude, longitude, safety_zones, user_id, timestamp)

def detect_unusual_movement(current_location, previous_locations, user_id):
    """Convenience function to detect unusual movement using default system"""
    return default_system.detect_unusual_movement(current_location, previous_locations, user_id)

def analyze_communication(message, user_id, context=None):
    """Convenience function to analyze communication using default system"""
    return default_system.analyze_communication(message, user_id, context)

# Lambda handler
def lambda_handler(event, context):
    """AWS Lambda handler function"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Check event type
        if "httpMethod" in event:
            # API Gateway event
            if event["httpMethod"] == "POST":
                body = json.loads(event.get("body", "{}"))
                path = event.get("path", "")
                
                if path.endswith("/location"):
                    # Location safety check
                    latitude = body.get("latitude")
                    longitude = body.get("longitude")
                    safety_zones = body.get("safety_zones", [])
                    user_id = body.get("user_id")
                    timestamp = body.get("timestamp")
                    
                    result = check_location_safety(latitude, longitude, safety_zones, user_id, timestamp)
                    
                elif path.endswith("/movement"):
                    # Movement analysis
                    current_location = body.get("current_location", {})
                    previous_locations = body.get("previous_locations", [])
                    user_id = body.get("user_id")
                    
                    result = detect_unusual_movement(current_location, previous_locations, user_id)
                    
                elif path.endswith("/communication"):
                    # Communication analysis
                    message = body.get("message", "")
                    user_id = body.get("user_id")
                    context = body.get("context")
                    
                    result = analyze_communication(message, user_id, context)
                    
                elif path.endswith("/report"):
                    # Generate safety report
                    user_id = body.get("user_id")
                    location_history = body.get("location_history", [])
                    safety_zones = body.get("safety_zones", [])
                    communication_history = body.get("communication_history", [])
                    timeframe_hours = body.get("timeframe_hours", 24)
                    
                    result = default_system.generate_safety_report(
                        user_id, location_history, safety_zones, 
                        communication_history, timeframe_hours
                    )
                    
                else:
                    return {
                        "statusCode": 400,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({"error": "Unsupported path"})
                    }
                    
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(result)
                }
                
            else:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Method not supported"})
                }
                
        elif "Records" in event:
            # SQS event
            for record in event["Records"]:
                body = json.loads(record["body"])
                
                # Process the alert based on type
                alert_type = body.get("alert_type")
                
                if alert_type == "location":
                    latitude = body.get("latitude")
                    longitude = body.get("longitude")
                    safety_zones = body.get("safety_zones", [])
                    user_id = body.get("user_id")
                    timestamp = body.get("timestamp")
                    
                    result = check_location_safety(latitude, longitude, safety_zones, user_id, timestamp)
                    logger.info(f"Processed location alert: {json.dumps(result)}")
                    
                elif alert_type == "movement":
                    current_location = body.get("current_location", {})
                    previous_locations = body.get("previous_locations", [])
                    user_id = body.get("user_id")
                    
                    result = detect_unusual_movement(current_location, previous_locations, user_id)
                    logger.info(f"Processed movement alert: {json.dumps(result)}")
                    
                elif alert_type == "communication":
                    message = body.get("message", "")
                    user_id = body.get("user_id")
                    context = body.get("context")
                    
                    result = analyze_communication(message, user_id, context)
                    logger.info(f"Processed communication alert: {json.dumps(result)}")
                    
                else:
                    logger.warning(f"Unknown alert type: {alert_type}")
                    
            return {"statusCode": 200, "body": "Processed SQS events"}
            
        else:
            # Direct invocation
            action = event.get("action", "")
            
            if action == "check_location":
                latitude = event.get("latitude")
                longitude = event.get("longitude")
                safety_zones = event.get("safety_zones", [])
                user_id = event.get("user_id")
                timestamp = event.get("timestamp")
                
                result = check_location_safety(latitude, longitude, safety_zones, user_id, timestamp)
                
            elif action == "detect_movement":
                current_location = event.get("current_location", {})
                previous_locations = event.get("previous_locations", [])
                user_id = event.get("user_id")
                
                result = detect_unusual_movement(current_location, previous_locations, user_id)
                
            elif action == "analyze_message":
                message = event.get("message", "")
                user_id = event.get("user_id")
                context = event.get("context")
                
                result = analyze_communication(message, user_id, context)
                
            elif action == "generate_report":
                user_id = event.get("user_id")
                location_history = event.get("location_history", [])
                safety_zones = event.get("safety_zones", [])
                communication_history = event.get("communication_history", [])
                timeframe_hours = event.get("timeframe_hours", 24)
                
                result = default_system.generate_safety_report(
                    user_id, location_history, safety_zones, 
                    communication_history, timeframe_hours
                )
                
            else:
                return {"error": "Unsupported action"}
                
            return result
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        
        if "httpMethod" in event:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Internal server error: {str(e)}"})
            }
        else:
            return {"error": f"Internal server error: {str(e)}"}


# For local testing
if __name__ == "__main__":
    import math  # For _distance_to_segment function
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Test data
    safety_zones = [
        {
            "name": "Home",
            "center": {"latitude": 37.7749, "longitude": -122.4194},
            "radius": 200  # meters
        },
        {
            "name": "Park",
            "polygon": [
                [37.7800, -122.4300],
                [37.7800, -122.4250],
                [37.7750, -122.4250],
                [37.7750, -122.4300]
            ]
        }
    ]
    
    # Test location check
    print("\nTesting location safety check:")
    result = check_location_safety(37.7749, -122.4194, safety_zones, "test_user")
    print(f"Inside zone: {json.dumps(result, indent=2)}")
    
    result = check_location_safety(37.8000, -122.5000, safety_zones, "test_user")
    print(f"Outside zone: {json.dumps(result, indent=2)}")
    
    # Test movement detection
    print("\nTesting unusual movement detection:")
    current_location = {"latitude": 37.7800, "longitude": -122.4300, "timestamp": datetime.datetime.utcnow().isoformat()}
    previous_locations = [
        {"latitude": 37.7749, "longitude": -122.4194, "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=5)).isoformat()}
    ]
    
    result = detect_unusual_movement(current_location, previous_locations, "test_user")
    print(f"Movement detection: {json.dumps(result, indent=2)}")
    
    # Test communication analysis
    print("\nTesting communication analysis:")
    result = analyze_communication("I'm feeling a bit confused today and not sure where I am.", "test_user")
    print(f"Communication analysis: {json.dumps(result, indent=2)}")
    
    result = analyze_communication("I'm having a great day at the park with my family.", "test_user")
    print(f"Communication analysis: {json.dumps(result, indent=2)}")
    
    print("\nTests completed.")