import os
import logging
import json
import hashlib
from datetime import datetime
import base64
import uuid
import numpy as np
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

class ARNavigationSystem:
    """
    Augmented Reality (AR) navigation and reminder system for dementia patients.
    Provides indoor navigation, object recognition, and contextual reminders.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Set up storage directories
        self.layouts_dir = os.path.join('data', 'ar_layouts')
        self.markers_dir = os.path.join('data', 'ar_markers')
        self.instructions_dir = os.path.join('data', 'ar_instructions')
        self.objects_dir = os.path.join('data', 'ar_objects')
        
        # Ensure directories exist
        os.makedirs(self.layouts_dir, exist_ok=True)
        os.makedirs(self.markers_dir, exist_ok=True)
        os.makedirs(self.instructions_dir, exist_ok=True)
        os.makedirs(self.objects_dir, exist_ok=True)
        
        # Load existing data
        self.location_layouts = self._load_layouts()
        self.object_definitions = self._load_object_definitions()
        self.navigation_paths = self._load_navigation_paths()
        self.reminder_markers = self._load_reminder_markers()
        
        self.logger.info("AR Navigation System initialized")
    
    def _load_layouts(self):
        """Load location layout data for indoor navigation."""
        try:
            layouts = {}
            layouts_path = os.path.join(self.layouts_dir, 'location_layouts.json')
            
            if os.path.exists(layouts_path):
                with open(layouts_path, 'r') as f:
                    layouts = json.load(f)
            
            self.logger.info(f"Loaded {len(layouts)} location layouts")
            return layouts
        except Exception as e:
            self.logger.error(f"Error loading layouts: {str(e)}")
            return {}
    
    def _save_layouts(self):
        """Save location layout data."""
        try:
            layouts_path = os.path.join(self.layouts_dir, 'location_layouts.json')
            with open(layouts_path, 'w') as f:
                json.dump(self.location_layouts, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving layouts: {str(e)}")
            return False
    
    def _load_object_definitions(self):
        """Load object definitions for object recognition."""
        try:
            objects = {}
            objects_path = os.path.join(self.objects_dir, 'object_definitions.json')
            
            if os.path.exists(objects_path):
                with open(objects_path, 'r') as f:
                    objects = json.load(f)
            
            self.logger.info(f"Loaded {len(objects)} object definitions")
            return objects
        except Exception as e:
            self.logger.error(f"Error loading object definitions: {str(e)}")
            return {}
    
    def _save_object_definitions(self):
        """Save object definitions."""
        try:
            objects_path = os.path.join(self.objects_dir, 'object_definitions.json')
            with open(objects_path, 'w') as f:
                json.dump(self.object_definitions, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving object definitions: {str(e)}")
            return False
    
    def _load_navigation_paths(self):
        """Load navigation paths between locations."""
        try:
            paths = {}
            paths_path = os.path.join(self.layouts_dir, 'navigation_paths.json')
            
            if os.path.exists(paths_path):
                with open(paths_path, 'r') as f:
                    paths = json.load(f)
            
            self.logger.info(f"Loaded {len(paths)} navigation paths")
            return paths
        except Exception as e:
            self.logger.error(f"Error loading navigation paths: {str(e)}")
            return {}
    
    def _save_navigation_paths(self):
        """Save navigation paths."""
        try:
            paths_path = os.path.join(self.layouts_dir, 'navigation_paths.json')
            with open(paths_path, 'w') as f:
                json.dump(self.navigation_paths, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving navigation paths: {str(e)}")
            return False
    
    def _load_reminder_markers(self):
        """Load reminder markers data."""
        try:
            markers = {}
            markers_path = os.path.join(self.markers_dir, 'reminder_markers.json')
            
            if os.path.exists(markers_path):
                with open(markers_path, 'r') as f:
                    markers = json.load(f)
            
            self.logger.info(f"Loaded {len(markers)} reminder markers")
            return markers
        except Exception as e:
            self.logger.error(f"Error loading reminder markers: {str(e)}")
            return {}
    
    def _save_reminder_markers(self):
        """Save reminder markers."""
        try:
            markers_path = os.path.join(self.markers_dir, 'reminder_markers.json')
            with open(markers_path, 'w') as f:
                json.dump(self.reminder_markers, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving reminder markers: {str(e)}")
            return False
    
    def add_location_layout(self, patient_id, location_name, layout_data, floor_plan_image=None):
        """
        Add a new location layout for indoor navigation.
        
        Args:
            patient_id: ID of the patient
            location_name: Name of the location (e.g., 'home', 'nursing_facility')
            layout_data: Dict with room and area definitions
            floor_plan_image: Optional base64 encoded floor plan image
            
        Returns:
            dict: The added location layout
        """
        try:
            # Generate ID for the layout
            layout_id = f"layout_{patient_id}_{location_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
            
            # Process floor plan image if provided
            image_filename = None
            if floor_plan_image:
                # Save base64 encoded image
                try:
                    # Remove data URL prefix if present
                    if ',' in floor_plan_image:
                        floor_plan_image = floor_plan_image.split(',')[1]
                    
                    # Decode base64 and save image
                    image_filename = f"{layout_id}.png"
                    image_path = os.path.join(self.layouts_dir, image_filename)
                    
                    img_data = base64.b64decode(floor_plan_image)
                    img = Image.open(BytesIO(img_data))
                    img.save(image_path)
                except Exception as e:
                    self.logger.error(f"Error saving floor plan image: {str(e)}")
            
            # Create layout object
            layout = {
                'id': layout_id,
                'patient_id': patient_id,
                'name': location_name,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'floor_plan_image': image_filename,
                'rooms': layout_data.get('rooms', []),
                'areas': layout_data.get('areas', []),
                'landmarks': layout_data.get('landmarks', []),
                'metadata': layout_data.get('metadata', {})
            }
            
            # Add to layouts dictionary
            self.location_layouts[layout_id] = layout
            
            # Save layouts
            self._save_layouts()
            
            self.logger.info(f"Added location layout '{location_name}' for patient {patient_id}")
            return layout
        
        except Exception as e:
            self.logger.error(f"Error adding location layout: {str(e)}")
            return None
    
    def add_navigation_path(self, layout_id, start_point, end_point, path_points, path_name=None, difficulty=None):
        """
        Add a navigation path between two points in a location layout.
        
        Args:
            layout_id: ID of the location layout
            start_point: Starting point coordinates and name
            end_point: Ending point coordinates and name
            path_points: List of waypoints along the path
            path_name: Optional name for the path
            difficulty: Optional difficulty rating (easy, medium, hard)
            
        Returns:
            dict: The added navigation path
        """
        try:
            # Check if layout exists
            if layout_id not in self.location_layouts:
                self.logger.error(f"Layout {layout_id} not found")
                return None
            
            # Generate path ID
            path_id = f"path_{layout_id}_{uuid.uuid4().hex[:8]}"
            
            # Default name if not provided
            if not path_name:
                path_name = f"Path from {start_point.get('name', 'Start')} to {end_point.get('name', 'End')}"
            
            # Create path object
            path = {
                'id': path_id,
                'layout_id': layout_id,
                'name': path_name,
                'start_point': start_point,
                'end_point': end_point,
                'path_points': path_points,
                'difficulty': difficulty or 'medium',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'metadata': {
                    'length': len(path_points),
                    'estimated_time': self._estimate_travel_time(path_points, difficulty)
                }
            }
            
            # Add to navigation paths
            self.navigation_paths[path_id] = path
            
            # Save navigation paths
            self._save_navigation_paths()
            
            self.logger.info(f"Added navigation path '{path_name}' for layout {layout_id}")
            return path
        
        except Exception as e:
            self.logger.error(f"Error adding navigation path: {str(e)}")
            return None
    
    def _estimate_travel_time(self, path_points, difficulty):
        """Estimate travel time based on path length and difficulty."""
        # Simple estimation: 3 seconds per point for easy, 5 for medium, 8 for hard
        difficulty_multipliers = {
            'easy': 3,
            'medium': 5,
            'hard': 8
        }
        
        multiplier = difficulty_multipliers.get(difficulty, 5)
        return len(path_points) * multiplier
    
    def add_reminder_marker(self, patient_id, location_id, marker_type, position, content, trigger_condition=None, expiration=None):
        """
        Add an AR reminder marker to a specific location.
        
        Args:
            patient_id: ID of the patient
            location_id: ID of the location layout
            marker_type: Type of marker (text, audio, video, instruction)
            position: Position coordinates of the marker
            content: Content of the reminder (text or media path)
            trigger_condition: Optional condition to trigger the reminder
            expiration: Optional expiration time for the reminder
            
        Returns:
            dict: The added reminder marker
        """
        try:
            # Check if layout exists
            if location_id not in self.location_layouts:
                self.logger.error(f"Layout {location_id} not found")
                return None
            
            # Generate marker ID
            marker_id = f"marker_{patient_id}_{uuid.uuid4().hex[:8]}"
            
            # Create marker object
            marker = {
                'id': marker_id,
                'patient_id': patient_id,
                'location_id': location_id,
                'marker_type': marker_type,
                'position': position,
                'content': content,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'trigger_condition': trigger_condition or 'proximity',
                'active': True
            }
            
            # Add expiration if provided
            if expiration:
                marker['expiration'] = expiration
            
            # Add to reminder markers
            self.reminder_markers[marker_id] = marker
            
            # Save reminder markers
            self._save_reminder_markers()
            
            self.logger.info(f"Added reminder marker for patient {patient_id} at location {location_id}")
            return marker
        
        except Exception as e:
            self.logger.error(f"Error adding reminder marker: {str(e)}")
            return None
    
    def add_object_definition(self, object_name, object_type, description, image_data=None, important=False):
        """
        Add an object definition for object recognition.
        
        Args:
            object_name: Name of the object
            object_type: Type/category of object
            description: Description of the object
            image_data: Optional base64 encoded image of the object
            important: Whether this is an important object to track
            
        Returns:
            dict: The added object definition
        """
        try:
            # Generate object ID
            object_id = f"object_{object_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
            
            # Process object image if provided
            image_filename = None
            if image_data:
                # Save base64 encoded image
                try:
                    # Remove data URL prefix if present
                    if ',' in image_data:
                        image_data = image_data.split(',')[1]
                    
                    # Decode base64 and save image
                    image_filename = f"{object_id}.png"
                    image_path = os.path.join(self.objects_dir, image_filename)
                    
                    img_data = base64.b64decode(image_data)
                    img = Image.open(BytesIO(img_data))
                    img.save(image_path)
                except Exception as e:
                    self.logger.error(f"Error saving object image: {str(e)}")
            
            # Create object definition
            object_def = {
                'id': object_id,
                'name': object_name,
                'type': object_type,
                'description': description,
                'image': image_filename,
                'important': important,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'recognition_data': {
                    'trained': image_filename is not None,
                    'confidence_threshold': 0.7 if important else 0.5
                }
            }
            
            # Add to object definitions
            self.object_definitions[object_id] = object_def
            
            # Save object definitions
            self._save_object_definitions()
            
            self.logger.info(f"Added object definition for '{object_name}'")
            return object_def
        
        except Exception as e:
            self.logger.error(f"Error adding object definition: {str(e)}")
            return None
    
    def generate_navigation_instructions(self, patient_id, layout_id, start_name, end_name, complexity='simple'):
        """
        Generate navigation instructions for a path.
        
        Args:
            patient_id: ID of the patient
            layout_id: ID of the location layout
            start_name: Name of starting point
            end_name: Name of ending point
            complexity: Instruction complexity (simple, moderate, detailed)
            
        Returns:
            dict: Navigation instructions
        """
        try:
            # Check if layout exists
            if layout_id not in self.location_layouts:
                self.logger.error(f"Layout {layout_id} not found")
                return None
            
            layout = self.location_layouts[layout_id]
            
            # Find matching path
            matching_paths = []
            for path_id, path in self.navigation_paths.items():
                if path['layout_id'] != layout_id:
                    continue
                
                start_matches = path['start_point'].get('name', '').lower() == start_name.lower()
                end_matches = path['end_point'].get('name', '').lower() == end_name.lower()
                
                if start_matches and end_matches:
                    matching_paths.append(path)
            
            if not matching_paths:
                self.logger.error(f"No path found from {start_name} to {end_name} in layout {layout_id}")
                return None
            
            # Use the first matching path (or could use some criteria to pick best)
            path = matching_paths[0]
            
            # Generate instructions based on complexity
            instructions = self._generate_path_instructions(path, complexity)
            
            # Create instruction object
            instruction_data = {
                'patient_id': patient_id,
                'layout_id': layout_id,
                'path_id': path['id'],
                'from': start_name,
                'to': end_name,
                'complexity': complexity,
                'instructions': instructions,
                'generated_at': datetime.utcnow().isoformat(),
                'estimated_time': path['metadata']['estimated_time'],
                'ar_markers': self._get_relevant_markers(patient_id, layout_id, path),
                'landmarks': self._extract_landmarks(layout, path)
            }
            
            self.logger.info(f"Generated navigation instructions from {start_name} to {end_name} for patient {patient_id}")
            return instruction_data
        
        except Exception as e:
            self.logger.error(f"Error generating navigation instructions: {str(e)}")
            return None
    
    def _generate_path_instructions(self, path, complexity):
        """Generate textual instructions for a path."""
        instructions = []
        
        # Get waypoints
        waypoints = path['path_points']
        
        if not waypoints:
            return [f"Go from {path['start_point'].get('name', 'Start')} to {path['end_point'].get('name', 'End')}."]
        
        # Generate instructions based on complexity
        if complexity == 'simple':
            # Simple instructions with minimal steps
            if len(waypoints) <= 3:
                instructions.append(f"Go from {path['start_point'].get('name', 'Start')} directly to {path['end_point'].get('name', 'End')}.")
            else:
                # Pick a few key waypoints
                key_points = [waypoints[0], waypoints[len(waypoints)//2], waypoints[-1]]
                
                for i, point in enumerate(key_points):
                    if i == 0:
                        instructions.append(f"Start at {path['start_point'].get('name', 'Start')}.")
                    elif i == len(key_points) - 1:
                        instructions.append(f"Go to {path['end_point'].get('name', 'End')}.")
                    else:
                        if 'landmark' in point:
                            instructions.append(f"Walk past {point['landmark']}.")
                        else:
                            instructions.append("Continue straight ahead.")
        
        elif complexity == 'moderate':
            # Moderate instructions with regular guidance
            instructions.append(f"Start at {path['start_point'].get('name', 'Start')}.")
            
            # Group waypoints into logical chunks
            chunk_size = max(1, len(waypoints) // 4)
            for i in range(0, len(waypoints), chunk_size):
                chunk = waypoints[i:i+chunk_size]
                last_in_chunk = chunk[-1]
                
                if 'landmark' in last_in_chunk:
                    instructions.append(f"Go to {last_in_chunk['landmark']}.")
                elif 'turn' in last_in_chunk:
                    instructions.append(f"Take a {last_in_chunk['turn']} turn.")
                elif i + chunk_size >= len(waypoints):
                    instructions.append(f"Continue until you reach {path['end_point'].get('name', 'End')}.")
                else:
                    instructions.append("Continue straight ahead.")
            
            if instructions[-1] != f"Continue until you reach {path['end_point'].get('name', 'End')}.":
                instructions.append(f"You have arrived at {path['end_point'].get('name', 'End')}.")
        
        else:  # detailed
            # Detailed instructions with step-by-step guidance
            instructions.append(f"Start at {path['start_point'].get('name', 'Start')}.")
            
            for i, point in enumerate(waypoints):
                if 'landmark' in point:
                    instructions.append(f"Walk to {point['landmark']}.")
                elif 'turn' in point:
                    instructions.append(f"Take a {point['turn']} turn.")
                elif i == len(waypoints) - 1:
                    instructions.append(f"Continue straight to {path['end_point'].get('name', 'End')}.")
                elif i % 2 == 0:  # Add periodic reassurance
                    instructions.append("Continue straight ahead.")
            
            instructions.append(f"You have arrived at {path['end_point'].get('name', 'End')}.")
        
        return instructions
    
    def _get_relevant_markers(self, patient_id, layout_id, path):
        """Get reminder markers relevant to a navigation path."""
        # Filter markers by patient and location
        relevant_markers = []
        
        for marker_id, marker in self.reminder_markers.items():
            if marker['patient_id'] == patient_id and marker['location_id'] == layout_id:
                # Check if marker is near the path
                if self._is_marker_near_path(marker, path):
                    relevant_markers.append(marker)
        
        return relevant_markers
    
    def _is_marker_near_path(self, marker, path):
        """Check if a marker is near a navigation path."""
        # Simple implementation: check if marker is within threshold distance of any path point
        marker_pos = marker['position']
        threshold = 5.0  # Distance threshold in arbitrary units
        
        for point in path['path_points']:
            if 'x' in point and 'y' in point:
                # Calculate distance
                dx = marker_pos.get('x', 0) - point.get('x', 0)
                dy = marker_pos.get('y', 0) - point.get('y', 0)
                distance = (dx**2 + dy**2)**0.5
                
                if distance <= threshold:
                    return True
        
        return False
    
    def _extract_landmarks(self, layout, path):
        """Extract landmarks along a navigation path."""
        landmarks = []
        
        # Get all landmarks from the layout
        layout_landmarks = layout.get('landmarks', [])
        
        # Check which landmarks are near the path
        for landmark in layout_landmarks:
            for point in path['path_points']:
                if 'landmark' in point and point['landmark'] == landmark['name']:
                    landmarks.append(landmark)
                    break
        
        return landmarks
    
    def get_active_reminders(self, patient_id, location_id=None, current_position=None):
        """
        Get active reminders for a patient at a specific location.
        
        Args:
            patient_id: ID of the patient
            location_id: Optional ID of the location layout
            current_position: Optional current position coordinates
            
        Returns:
            list: Active reminder markers
        """
        try:
            # Filter reminders by patient
            patient_reminders = [
                marker for marker_id, marker in self.reminder_markers.items()
                if marker['patient_id'] == patient_id and marker['active']
            ]
            
            # Filter by location if provided
            if location_id:
                patient_reminders = [
                    marker for marker in patient_reminders
                    if marker['location_id'] == location_id
                ]
            
            # Filter by proximity if position provided
            if current_position:
                threshold = 10.0  # Distance threshold in arbitrary units
                
                # Keep only markers within threshold distance
                nearby_reminders = []
                for marker in patient_reminders:
                    marker_pos = marker['position']
                    
                    # Calculate distance
                    dx = marker_pos.get('x', 0) - current_position.get('x', 0)
                    dy = marker_pos.get('y', 0) - current_position.get('y', 0)
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance <= threshold:
                        # Add distance info to marker
                        marker_copy = marker.copy()
                        marker_copy['distance'] = distance
                        nearby_reminders.append(marker_copy)
                
                # Sort by distance
                nearby_reminders.sort(key=lambda m: m['distance'])
                return nearby_reminders
            
            return patient_reminders
        
        except Exception as e:
            self.logger.error(f"Error getting active reminders: {str(e)}")
            return []
    
    def detect_objects(self, patient_id, image_data, location_id=None):
        """
        Detect and identify objects in an image.
        
        Args:
            patient_id: ID of the patient
            image_data: Base64 encoded image data
            location_id: Optional ID of the location layout for context
            
        Returns:
            dict: Detected objects with confidence scores
        """
        try:
            # In a real implementation, this would use computer vision models
            # For this prototype, we'll simulate object detection with random results
            
            # Get all object definitions
            all_objects = list(self.object_definitions.values())
            
            # If no objects defined, return empty result
            if not all_objects:
                return {
                    'success': True,
                    'objects_detected': [],
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Simulate detection: randomly select 1-3 objects with random confidence
            num_detected = min(len(all_objects), np.random.randint(1, 4))
            detected_indices = np.random.choice(len(all_objects), num_detected, replace=False)
            
            detected_objects = []
            for idx in detected_indices:
                obj = all_objects[idx]
                
                # Generate random confidence (higher for important objects)
                base_confidence = 0.7 if obj['important'] else 0.5
                confidence = min(0.99, base_confidence + np.random.uniform(0, 0.3))
                
                detected_objects.append({
                    'id': obj['id'],
                    'name': obj['name'],
                    'type': obj['type'],
                    'confidence': confidence,
                    'description': obj['description'],
                    'important': obj['important'],
                    'bounding_box': {
                        'x': np.random.uniform(0.1, 0.9),
                        'y': np.random.uniform(0.1, 0.9),
                        'width': np.random.uniform(0.1, 0.3),
                        'height': np.random.uniform(0.1, 0.3)
                    }
                })
            
            # Sort by confidence (highest first)
            detected_objects.sort(key=lambda o: o['confidence'], reverse=True)
            
            return {
                'success': True,
                'objects_detected': detected_objects,
                'timestamp': datetime.utcnow().isoformat(),
                'context': {
                    'patient_id': patient_id,
                    'location_id': location_id
                }
            }
        
        except Exception as e:
            self.logger.error(f"Error detecting objects: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_patient_layouts(self, patient_id):
        """
        Get all location layouts for a patient.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            list: Location layouts for the patient
        """
        try:
            # Filter layouts by patient
            patient_layouts = [
                layout for layout_id, layout in self.location_layouts.items()
                if layout['patient_id'] == patient_id
            ]
            
            return patient_layouts
        
        except Exception as e:
            self.logger.error(f"Error getting patient layouts: {str(e)}")
            return []