"""
AlphaWolf Utility Functions
Part of The Christman AI Project - LumaCognify AI

This module provides common utility functions used by other AlphaWolf modules.

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
from typing import Dict, List, Any, Optional, Tuple, Union, Callable

# Configure logging
logger = logging.getLogger(__name__)

def generate_unique_id(prefix: str = "id") -> str:
    """
    Generate a unique identifier with optional prefix
    
    Parameters:
    - prefix: Optional string prefix for the ID
    
    Returns:
    - Unique ID string
    """
    random_part = str(uuid.uuid4())
    timestamp = int(time.time() * 1000)
    return f"{prefix}_{timestamp}_{random_part[:8]}"
    
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the Haversine distance between two points in meters
    
    Parameters:
    - lat1, lon1: Coordinates of the first point
    - lat2, lon2: Coordinates of the second point
    
    Returns:
    - Distance in meters
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Radius of the Earth in meters
    R = 6371000
    
    # Convert to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance
    
def is_inside_polygon(lat: float, lon: float, polygon_points: List[Tuple[float, float]]) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm
    
    Parameters:
    - lat, lon: Coordinates of the point to check
    - polygon_points: List of (lat, lon) tuples forming the polygon
    
    Returns:
    - True if the point is inside the polygon, False otherwise
    """
    # Ray casting algorithm
    inside = False
    j = len(polygon_points) - 1
    
    for i in range(len(polygon_points)):
        if ((polygon_points[i][1] > lon) != (polygon_points[j][1] > lon)) and \
           (lat < (polygon_points[j][0] - polygon_points[i][0]) * 
           (lon - polygon_points[i][1]) / (polygon_points[j][1] - polygon_points[i][1]) + 
           polygon_points[i][0]):
            inside = not inside
        j = i
        
    return inside
    
def safe_get(obj: Any, key_path: str, default: Any = None) -> Any:
    """
    Safely navigate nested objects with dot notation
    
    Parameters:
    - obj: The object to navigate
    - key_path: Dot-separated path of keys (e.g., "user.profile.name")
    - default: Default value if path doesn't exist
    
    Returns:
    - Value at the path or default if not found
    """
    if obj is None:
        return default
        
    keys = key_path.split(".")
    current = obj
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif hasattr(current, key):
            current = getattr(current, key)
        else:
            return default
            
    return current
    
def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Check if latitude and longitude are valid
    
    Parameters:
    - lat: Latitude to validate
    - lon: Longitude to validate
    
    Returns:
    - True if valid, False otherwise
    """
    try:
        lat_float = float(lat)
        lon_float = float(lon)
        
        return -90.0 <= lat_float <= 90.0 and -180.0 <= lon_float <= 180.0
    except (ValueError, TypeError):
        return False
        
def format_timestamp(timestamp: Optional[Union[str, datetime.datetime, float, int]] = None,
                    format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a timestamp in a human-readable way
    
    Parameters:
    - timestamp: Timestamp to format (string ISO format, datetime, or unix timestamp)
                 If None, use current time
    - format_str: Format string for strftime
    
    Returns:
    - Formatted timestamp string
    """
    if timestamp is None:
        dt = datetime.datetime.utcnow()
    elif isinstance(timestamp, datetime.datetime):
        dt = timestamp
    elif isinstance(timestamp, (int, float)):
        dt = datetime.datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp, str):
        try:
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            try:
                dt = datetime.datetime.strptime(timestamp, format_str)
            except ValueError:
                try:
                    # Try unix timestamp as string
                    dt = datetime.datetime.fromtimestamp(float(timestamp))
                except (ValueError, TypeError):
                    logger.error(f"Unable to parse timestamp: {timestamp}")
                    return str(timestamp)
    else:
        logger.error(f"Unsupported timestamp type: {type(timestamp)}")
        return str(timestamp)
        
    return dt.strftime(format_str)
    
def clean_text(text: str) -> str:
    """
    Clean text by removing excess whitespace, control characters, etc.
    
    Parameters:
    - text: Text to clean
    
    Returns:
    - Cleaned text
    """
    if not text:
        return ""
        
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters
    text = ''.join(c for c in text if c.isprintable() or c.isspace())
    
    # Trim leading/trailing whitespace
    return text.strip()
    
def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding a suffix if truncated
    
    Parameters:
    - text: Text to truncate
    - max_length: Maximum length of the resulting text
    - suffix: Suffix to add if truncated
    
    Returns:
    - Truncated text
    """
    if not text:
        return ""
        
    if len(text) <= max_length:
        return text
        
    # Truncate and add suffix
    return text[:max_length-len(suffix)] + suffix
    
def retry(max_attempts: int = 3, 
         delay_seconds: float = 1.0, 
         backoff_factor: float = 2.0,
         exceptions_to_retry: Tuple[Exception, ...] = (Exception,)) -> Callable:
    """
    Decorator for retrying functions that might fail
    
    Parameters:
    - max_attempts: Maximum number of retry attempts
    - delay_seconds: Initial delay between attempts
    - backoff_factor: Factor to increase delay by after each failure
    - exceptions_to_retry: Tuple of exceptions that should trigger a retry
    
    Returns:
    - Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            delay = delay_seconds
            
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions_to_retry as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise
                        
                    logger.warning(f"Retry {attempts}/{max_attempts} for {func.__name__} after error: {e}")
                    time.sleep(delay)
                    delay *= backoff_factor
                    
        return wrapper
    return decorator
    
def hash_data(data: Any) -> str:
    """
    Generate a hash of data
    
    Parameters:
    - data: Data to hash (will be JSON serialized if not a string)
    
    Returns:
    - Hash string
    """
    if not isinstance(data, str):
        try:
            data = json.dumps(data, sort_keys=True)
        except (TypeError, ValueError):
            data = str(data)
            
    return hashlib.md5(data.encode()).hexdigest()
    
def merge_dicts(dict1: Dict, dict2: Dict, overwrite: bool = True) -> Dict:
    """
    Recursively merge two dictionaries
    
    Parameters:
    - dict1: First dictionary
    - dict2: Second dictionary (values override dict1 if overwrite=True)
    - overwrite: Whether to overwrite existing values
    
    Returns:
    - Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value, overwrite)
        elif key not in result or overwrite:
            result[key] = value
            
    return result
    
def batch_process(items: List[Any], 
                 processor_func: Callable[[Any], Any], 
                 batch_size: int = 10,
                 progress_callback: Optional[Callable[[int, int], None]] = None) -> List[Any]:
    """
    Process a list of items in batches
    
    Parameters:
    - items: List of items to process
    - processor_func: Function to apply to each item
    - batch_size: Number of items to process in each batch
    - progress_callback: Optional callback function to report progress
    
    Returns:
    - List of processed items
    """
    results = []
    total_items = len(items)
    
    for i in range(0, total_items, batch_size):
        batch = items[i:i+batch_size]
        batch_results = [processor_func(item) for item in batch]
        results.extend(batch_results)
        
        # Report progress if callback provided
        if progress_callback:
            items_processed = min(i + batch_size, total_items)
            progress_callback(items_processed, total_items)
            
    return results
    
def create_directory_if_not_exists(directory: str) -> bool:
    """
    Create a directory if it doesn't exist
    
    Parameters:
    - directory: Path to directory
    
    Returns:
    - True if directory exists or was created, False on error
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False
        
def is_valid_email(email: str) -> bool:
    """
    Check if a string is a valid email address
    
    Parameters:
    - email: Email string to validate
    
    Returns:
    - True if valid, False otherwise
    """
    # Simple regex for email validation
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))
    
def parse_duration(duration_str: str) -> Optional[datetime.timedelta]:
    """
    Parse a duration string into a timedelta
    
    Parameters:
    - duration_str: Duration string (e.g., "1h30m", "2d", "45s")
    
    Returns:
    - Timedelta object or None if invalid
    """
    try:
        # Regex for duration components
        pattern = re.compile(r'((?P<weeks>\d+)w)?((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?')
        match = pattern.match(duration_str)
        
        if not match:
            return None
            
        parts = match.groupdict()
        time_params = {}
        
        for name, param in parts.items():
            if param:
                time_params[name] = int(param)
                
        return datetime.timedelta(**time_params)
    except Exception as e:
        logger.error(f"Error parsing duration {duration_str}: {e}")
        return None