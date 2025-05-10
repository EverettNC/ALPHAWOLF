import logging
import os
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

class SymbolBoard:
    """
    Represents a personalized symbol communication board for a patient
    with various categories and symbols.
    """
    
    def __init__(self, patient_id: str, name: str, id: Optional[str] = None):
        """
        Initialize a symbol board.
        
        Args:
            patient_id: ID of the patient
            name: Name of the board
            id: Optional ID, will generate UUID if not provided
        """
        self.id = id or str(uuid.uuid4())
        self.patient_id = patient_id
        self.name = name
        self.categories: List[Dict[str, Any]] = []
        self.created_at = time.time()
        self.updated_at = time.time()
        self.layout = "grid"  # grid, list, custom
        self.style = {
            "backgroundColor": "#FFFFFF",
            "categoryBackgroundColor": "#F5F5F5",
            "symbolBorderColor": "#DDDDDD",
            "highlightColor": "#4A90E2",
            "textColor": "#333333",
            "fontSize": "medium"  # small, medium, large
        }
    
    def add_category(self, name: str, color: Optional[str] = None, 
                    icon: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new category to the board.
        
        Args:
            name: Category name
            color: Optional color code
            icon: Optional icon name or URL
            
        Returns:
            The added category
        """
        category = {
            "id": str(uuid.uuid4()),
            "name": name,
            "color": color or "#EEEEEE",
            "icon": icon,
            "symbols": []
        }
        
        self.categories.append(category)
        self.updated_at = time.time()
        return category
    
    def add_symbol(self, category_id: str, text: str, image_url: Optional[str] = None,
                 audio_url: Optional[str] = None, position: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Add a symbol to a category.
        
        Args:
            category_id: ID of the category
            text: Symbol text
            image_url: Optional URL to symbol image
            audio_url: Optional URL to audio pronunciation
            position: Optional position in the category
            
        Returns:
            The added symbol or None if category not found
        """
        for category in self.categories:
            if category["id"] == category_id:
                symbol = {
                    "id": str(uuid.uuid4()),
                    "text": text,
                    "image_url": image_url,
                    "audio_url": audio_url,
                    "created_at": time.time(),
                    "usage_count": 0
                }
                
                if position is not None and 0 <= position <= len(category["symbols"]):
                    category["symbols"].insert(position, symbol)
                else:
                    category["symbols"].append(symbol)
                
                self.updated_at = time.time()
                return symbol
        
        return None
    
    def remove_symbol(self, category_id: str, symbol_id: str) -> bool:
        """
        Remove a symbol from a category.
        
        Args:
            category_id: ID of the category
            symbol_id: ID of the symbol
            
        Returns:
            True if removed, False if not found
        """
        for category in self.categories:
            if category["id"] == category_id:
                for i, symbol in enumerate(category["symbols"]):
                    if symbol["id"] == symbol_id:
                        category["symbols"].pop(i)
                        self.updated_at = time.time()
                        return True
        
        return False
    
    def increment_symbol_usage(self, category_id: str, symbol_id: str) -> bool:
        """
        Increment usage count for a symbol.
        
        Args:
            category_id: ID of the category
            symbol_id: ID of the symbol
            
        Returns:
            True if updated, False if not found
        """
        for category in self.categories:
            if category["id"] == category_id:
                for symbol in category["symbols"]:
                    if symbol["id"] == symbol_id:
                        symbol["usage_count"] = symbol.get("usage_count", 0) + 1
                        self.updated_at = time.time()
                        return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "name": self.name,
            "categories": self.categories,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "layout": self.layout,
            "style": self.style
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SymbolBoard':
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation
            
        Returns:
            SymbolBoard instance
        """
        board = cls(
            patient_id=data["patient_id"],
            name=data["name"],
            id=data["id"]
        )
        
        board.categories = data["categories"]
        board.created_at = data["created_at"]
        board.updated_at = data["updated_at"]
        board.layout = data.get("layout", "grid")
        board.style = data.get("style", board.style)
        
        return board


class SymbolBoardService:
    """
    Service for managing personalized symbol communication boards for patients.
    Supports cloud storage and caching for low-latency delivery.
    """
    
    def __init__(self):
        """Initialize the symbol board service."""
        self.logger = logging.getLogger(__name__)
        
        # In-memory cache of symbol boards
        self.boards_cache: Dict[str, SymbolBoard] = {}
        
        # S3 configuration for persistence
        self.use_s3 = False
        self.s3_client = None
        self.s3_bucket = os.environ.get('SYMBOL_S3_BUCKET')
        self.s3_prefix = 'symbol_boards/'
        
        if self.s3_bucket:
            try:
                self.s3_client = boto3.client('s3')
                self.use_s3 = True
                self.logger.info(f"S3 storage enabled for symbol boards: {self.s3_bucket}")
            except Exception as e:
                self.logger.error(f"Failed to initialize S3 client: {str(e)}")
                self.use_s3 = False
        
        # CloudFront configuration for content delivery
        self.use_cloudfront = False
        self.cloudfront_domain = os.environ.get('CLOUDFRONT_DOMAIN')
        self.cloudfront_client = None
        
        if self.cloudfront_domain:
            try:
                self.cloudfront_client = boto3.client('cloudfront')
                self.use_cloudfront = True
                self.logger.info(f"CloudFront CDN enabled: {self.cloudfront_domain}")
            except Exception as e:
                self.logger.error(f"Failed to initialize CloudFront client: {str(e)}")
                self.use_cloudfront = False
        
        # Default symbol sets
        self.default_symbols: Dict[str, List[Dict[str, Any]]] = self._load_default_symbols()
        
        self.logger.info("Symbol board service initialized")
    
    def _load_default_symbols(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load default symbol sets for different categories.
        
        Returns:
            Dictionary of categories with default symbols
        """
        default_symbols = {
            "basic_needs": [
                {"text": "Water", "image_url": "symbols/water.svg"},
                {"text": "Food", "image_url": "symbols/food.svg"},
                {"text": "Bathroom", "image_url": "symbols/bathroom.svg"},
                {"text": "Sleep", "image_url": "symbols/sleep.svg"},
                {"text": "Medicine", "image_url": "symbols/medicine.svg"}
            ],
            "emotions": [
                {"text": "Happy", "image_url": "symbols/happy.svg"},
                {"text": "Sad", "image_url": "symbols/sad.svg"},
                {"text": "Angry", "image_url": "symbols/angry.svg"},
                {"text": "Scared", "image_url": "symbols/scared.svg"},
                {"text": "Confused", "image_url": "symbols/confused.svg"}
            ],
            "actions": [
                {"text": "Help", "image_url": "symbols/help.svg"},
                {"text": "Stop", "image_url": "symbols/stop.svg"},
                {"text": "More", "image_url": "symbols/more.svg"},
                {"text": "Less", "image_url": "symbols/less.svg"},
                {"text": "Wait", "image_url": "symbols/wait.svg"}
            ],
            "people": [
                {"text": "Me", "image_url": "symbols/me.svg"},
                {"text": "You", "image_url": "symbols/you.svg"},
                {"text": "Family", "image_url": "symbols/family.svg"},
                {"text": "Doctor", "image_url": "symbols/doctor.svg"},
                {"text": "Caregiver", "image_url": "symbols/caregiver.svg"}
            ],
            "time": [
                {"text": "Now", "image_url": "symbols/now.svg"},
                {"text": "Later", "image_url": "symbols/later.svg"},
                {"text": "Morning", "image_url": "symbols/morning.svg"},
                {"text": "Afternoon", "image_url": "symbols/afternoon.svg"},
                {"text": "Night", "image_url": "symbols/night.svg"}
            ]
        }
        
        return default_symbols
    
    def get_board(self, board_id: str, refresh_cache: bool = False) -> Optional[SymbolBoard]:
        """
        Get a symbol board by ID.
        
        Args:
            board_id: ID of the board
            refresh_cache: Whether to refresh the cache
            
        Returns:
            SymbolBoard or None if not found
        """
        # Check memory cache first if not refreshing
        if not refresh_cache and board_id in self.boards_cache:
            self.logger.debug(f"Cache hit for board {board_id}")
            return self.boards_cache[board_id]
        
        # Try to load from S3
        if self.use_s3 and self.s3_client:
            try:
                s3_key = f"{self.s3_prefix}{board_id}.json"
                response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=s3_key)
                data = json.loads(response['Body'].read().decode('utf-8'))
                
                board = SymbolBoard.from_dict(data)
                
                # Update cache
                self.boards_cache[board_id] = board
                
                self.logger.debug(f"Loaded board {board_id} from S3")
                return board
                
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchKey':
                    self.logger.error(f"Error retrieving board {board_id} from S3: {str(e)}")
            except Exception as e:
                self.logger.error(f"Error parsing board {board_id} from S3: {str(e)}")
        
        self.logger.debug(f"Board {board_id} not found")
        return None
    
    def get_boards_for_patient(self, patient_id: str) -> List[SymbolBoard]:
        """
        Get all symbol boards for a patient.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            List of SymbolBoard objects
        """
        boards = []
        
        # Try to list from S3
        if self.use_s3 and self.s3_client:
            try:
                # S3 doesn't support filtering by patient_id, so we need to list all and filter
                s3_prefix = self.s3_prefix
                paginator = self.s3_client.get_paginator('list_objects_v2')
                
                for page in paginator.paginate(Bucket=self.s3_bucket, Prefix=s3_prefix):
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            try:
                                # Get the board ID from the key
                                key = obj['Key']
                                board_id = key.replace(self.s3_prefix, '').replace('.json', '')
                                
                                # Get the board
                                board = self.get_board(board_id)
                                
                                # Filter by patient_id
                                if board and board.patient_id == patient_id:
                                    boards.append(board)
                            except Exception as e:
                                self.logger.error(f"Error processing S3 object {obj['Key']}: {str(e)}")
                
                self.logger.debug(f"Loaded {len(boards)} boards for patient {patient_id} from S3")
                
            except Exception as e:
                self.logger.error(f"Error listing boards for patient {patient_id} from S3: {str(e)}")
                
                # Fall back to memory cache
                for board in self.boards_cache.values():
                    if board.patient_id == patient_id:
                        boards.append(board)
        else:
            # Use memory cache only
            for board in self.boards_cache.values():
                if board.patient_id == patient_id:
                    boards.append(board)
        
        return boards
    
    def create_board(self, patient_id: str, name: str) -> SymbolBoard:
        """
        Create a new symbol board with default categories.
        
        Args:
            patient_id: ID of the patient
            name: Name of the board
            
        Returns:
            The created SymbolBoard
        """
        board = SymbolBoard(patient_id=patient_id, name=name)
        
        # Add default categories and symbols
        for category_name, symbols in self.default_symbols.items():
            category = board.add_category(
                name=category_name.replace('_', ' ').title(),
                color=self._get_category_color(category_name)
            )
            
            for symbol in symbols:
                board.add_symbol(
                    category_id=category["id"],
                    text=symbol["text"],
                    image_url=symbol.get("image_url")
                )
        
        # Save the new board
        self.save_board(board)
        
        return board
    
    def save_board(self, board: SymbolBoard) -> bool:
        """
        Save a symbol board to storage.
        
        Args:
            board: SymbolBoard to save
            
        Returns:
            bool: Success of the operation
        """
        # Update timestamps
        board.updated_at = time.time()
        
        # Update memory cache
        self.boards_cache[board.id] = board
        
        # Save to S3 if enabled
        if self.use_s3 and self.s3_client:
            try:
                s3_key = f"{self.s3_prefix}{board.id}.json"
                
                # Convert to JSON
                board_json = json.dumps(board.to_dict())
                
                # Upload to S3
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=s3_key,
                    Body=board_json,
                    ContentType='application/json'
                )
                
                self.logger.debug(f"Saved board {board.id} to S3")
                
                # Invalidate CloudFront cache if enabled
                if self.use_cloudfront and self.cloudfront_client:
                    try:
                        self.cloudfront_client.create_invalidation(
                            DistributionId=self.cloudfront_domain,
                            InvalidationBatch={
                                'Paths': {
                                    'Quantity': 1,
                                    'Items': [f"/{s3_key}"]
                                },
                                'CallerReference': str(time.time())
                            }
                        )
                        self.logger.debug(f"Invalidated CloudFront cache for board {board.id}")
                    except Exception as e:
                        self.logger.error(f"Error invalidating CloudFront cache for board {board.id}: {str(e)}")
                
                return True
                
            except Exception as e:
                self.logger.error(f"Error saving board {board.id} to S3: {str(e)}")
                return False
        
        return True
    
    def delete_board(self, board_id: str) -> bool:
        """
        Delete a symbol board.
        
        Args:
            board_id: ID of the board to delete
            
        Returns:
            bool: Success of the operation
        """
        # Remove from memory cache
        if board_id in self.boards_cache:
            del self.boards_cache[board_id]
        
        # Remove from S3 if enabled
        if self.use_s3 and self.s3_client:
            try:
                s3_key = f"{self.s3_prefix}{board_id}.json"
                
                # Delete from S3
                self.s3_client.delete_object(Bucket=self.s3_bucket, Key=s3_key)
                
                self.logger.debug(f"Deleted board {board_id} from S3")
                
                # Invalidate CloudFront cache if enabled
                if self.use_cloudfront and self.cloudfront_client:
                    try:
                        self.cloudfront_client.create_invalidation(
                            DistributionId=self.cloudfront_domain,
                            InvalidationBatch={
                                'Paths': {
                                    'Quantity': 1,
                                    'Items': [f"/{s3_key}"]
                                },
                                'CallerReference': str(time.time())
                            }
                        )
                        self.logger.debug(f"Invalidated CloudFront cache for board {board_id}")
                    except Exception as e:
                        self.logger.error(f"Error invalidating CloudFront cache for board {board_id}: {str(e)}")
                
                return True
                
            except Exception as e:
                self.logger.error(f"Error deleting board {board_id} from S3: {str(e)}")
                return False
        
        return True
    
    def get_most_used_symbols(self, patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most frequently used symbols for a patient across all boards.
        
        Args:
            patient_id: ID of the patient
            limit: Maximum number of symbols to return
            
        Returns:
            List of symbol dictionaries with usage_count
        """
        # Get all boards for the patient
        boards = self.get_boards_for_patient(patient_id)
        
        # Collect symbols from all boards
        symbols_with_usage: List[Dict[str, Any]] = []
        
        for board in boards:
            for category in board.categories:
                for symbol in category["symbols"]:
                    # Add board and category info to the symbol
                    symbol_with_context = symbol.copy()
                    symbol_with_context["board_id"] = board.id
                    symbol_with_context["board_name"] = board.name
                    symbol_with_context["category_id"] = category["id"]
                    symbol_with_context["category_name"] = category["name"]
                    
                    symbols_with_usage.append(symbol_with_context)
        
        # Sort by usage count descending
        symbols_with_usage.sort(key=lambda s: s.get("usage_count", 0), reverse=True)
        
        # Return top symbols
        return symbols_with_usage[:limit]
    
    def get_symbol_suggestions(self, patient_id: str, context: Optional[str] = None, 
                             limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get symbol suggestions for a patient based on context and usage.
        
        Args:
            patient_id: ID of the patient
            context: Optional context hint (e.g., "food", "emotions")
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested symbols
        """
        # Get most used symbols as a base
        suggestions = self.get_most_used_symbols(patient_id, limit=limit*2)
        
        # If context is provided, try to prioritize symbols from that context
        if context:
            context_lower = context.lower()
            
            # Find symbols that match the context in text or category
            context_matches = []
            for symbol in suggestions:
                symbol_text = symbol.get("text", "").lower()
                category_name = symbol.get("category_name", "").lower()
                
                if (context_lower in symbol_text or 
                    context_lower in category_name):
                    context_matches.append(symbol)
            
            # Add other symbols from categories that match the context
            boards = self.get_boards_for_patient(patient_id)
            for board in boards:
                for category in board.categories:
                    category_name = category.get("name", "").lower()
                    
                    if context_lower in category_name:
                        for symbol in category.get("symbols", []):
                            # Add board and category info
                            symbol_with_context = symbol.copy()
                            symbol_with_context["board_id"] = board.id
                            symbol_with_context["board_name"] = board.name
                            symbol_with_context["category_id"] = category["id"]
                            symbol_with_context["category_name"] = category["name"]
                            
                            if symbol_with_context not in context_matches:
                                context_matches.append(symbol_with_context)
            
            # Combine context matches with most used symbols
            combined = context_matches + [s for s in suggestions if s not in context_matches]
            
            # Return top suggestions
            return combined[:limit]
        
        # Without context, just return most used symbols
        return suggestions[:limit]
    
    def upload_custom_symbol(self, patient_id: str, image_data: bytes, 
                          content_type: str, text: str) -> Tuple[bool, Optional[str]]:
        """
        Upload a custom symbol image.
        
        Args:
            patient_id: ID of the patient
            image_data: Image binary data
            content_type: Image MIME type
            text: Symbol text
            
        Returns:
            Tuple of (success, image_url)
        """
        if not self.use_s3 or not self.s3_client:
            self.logger.error("S3 not configured, cannot upload custom symbol")
            return (False, None)
        
        try:
            # Generate a unique filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{patient_id}_{timestamp}_{text.lower().replace(' ', '_')}"
            
            # Add appropriate extension
            if content_type == 'image/jpeg':
                filename += '.jpg'
            elif content_type == 'image/png':
                filename += '.png'
            elif content_type == 'image/svg+xml':
                filename += '.svg'
            else:
                filename += '.img'
            
            # Upload to S3
            s3_key = f"custom_symbols/{patient_id}/{filename}"
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=image_data,
                ContentType=content_type
            )
            
            # Generate URL
            if self.use_cloudfront and self.cloudfront_domain:
                image_url = f"https://{self.cloudfront_domain}/{s3_key}"
            else:
                image_url = f"https://{self.s3_bucket}.s3.amazonaws.com/{s3_key}"
            
            self.logger.info(f"Uploaded custom symbol for patient {patient_id}: {image_url}")
            
            return (True, image_url)
            
        except Exception as e:
            self.logger.error(f"Error uploading custom symbol for patient {patient_id}: {str(e)}")
            return (False, None)
    
    def _get_category_color(self, category_name: str) -> str:
        """
        Get a color for a category based on its name.
        
        Args:
            category_name: Category name
            
        Returns:
            Color code
        """
        # Simple mapping of category names to colors
        colors = {
            "basic_needs": "#FF9999",
            "emotions": "#FFCC99",
            "actions": "#CCFF99",
            "people": "#99CCFF",
            "time": "#CC99FF",
            "places": "#99FFCC",
            "objects": "#FFFF99",
            "descriptors": "#FF99CC",
            "food": "#99FFFF",
            "health": "#FFD700"
        }
        
        return colors.get(category_name, "#EEEEEE")