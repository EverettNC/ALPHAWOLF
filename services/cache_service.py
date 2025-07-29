import logging
import os
import json
import time
import hashlib
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

class CacheService:
    """
    Service for caching frequently accessed data to improve performance.
    Implements adaptive caching with expiration based on usage patterns.
    """
    
    def __init__(self):
        """Initialize the cache service."""
        self.logger = logging.getLogger(__name__)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_default = 300  # Default TTL of 5 minutes
        
        # S3 configuration for persistent caching
        self.use_s3 = False
        self.s3_bucket = os.environ.get('CACHE_S3_BUCKET')
        self.s3_prefix = 'cache/'
        
        if self.s3_bucket:
            try:
                self.s3_client = boto3.client('s3')
                self.use_s3 = True
                self.logger.info(f"S3 caching enabled using bucket: {self.s3_bucket}")
            except Exception as e:
                self.logger.error(f"Failed to initialize S3 client: {str(e)}")
                self.use_s3 = False
        
        self.logger.info("Cache service initialized")
    
    def get(self, key: str, namespace: str = 'default') -> Optional[Any]:
        """
        Get a value from the cache by key and namespace.
        
        Args:
            key: The cache key
            namespace: The namespace for the key (e.g., 'symbols', 'articles')
            
        Returns:
            The cached value or None if not found or expired
        """
        cache_key = self._make_cache_key(key, namespace)
        
        # First check memory cache
        if cache_key in self.memory_cache:
            cache_item = self.memory_cache[cache_key]
            
            # Check if item is expired
            if time.time() < cache_item.get('expires_at', 0):
                # Update last access time
                self.memory_cache[cache_key]['last_accessed'] = time.time()
                self.logger.debug(f"Cache hit for {namespace}/{key}")
                return cache_item['value']
            else:
                # Remove expired item
                del self.memory_cache[cache_key]
                self.logger.debug(f"Cache expired for {namespace}/{key}")
        
        # If not in memory, check S3 for persistent items
        if self.use_s3:
            try:
                s3_key = f"{self.s3_prefix}{namespace}/{cache_key}"
                response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=s3_key)
                
                # Get metadata
                metadata = response.get('Metadata', {})
                expires_at = float(metadata.get('expires-at', 0))
                
                # Check if expired
                if time.time() < expires_at:
                    # Load content from S3
                    content = response['Body'].read().decode('utf-8')
                    data = json.loads(content)
                    
                    # Update last accessed time in S3
                    self._update_s3_metadata(s3_key, {'last-accessed': str(time.time())})
                    
                    # Also cache in memory for faster access
                    self.memory_cache[cache_key] = {
                        'value': data,
                        'expires_at': expires_at,
                        'last_accessed': time.time()
                    }
                    
                    self.logger.debug(f"S3 cache hit for {namespace}/{key}")
                    return data
                else:
                    # Delete expired object
                    self.s3_client.delete_object(Bucket=self.s3_bucket, Key=s3_key)
                    self.logger.debug(f"S3 cache expired for {namespace}/{key}")
            
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchKey':
                    self.logger.error(f"S3 cache error: {str(e)}")
            except Exception as e:
                self.logger.error(f"Error retrieving from S3 cache: {str(e)}")
        
        self.logger.debug(f"Cache miss for {namespace}/{key}")
        return None
    
    def set(self, key: str, value: Any, namespace: str = 'default', ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache with a given TTL.
        
        Args:
            key: The cache key
            value: The value to cache
            namespace: The namespace for the key
            ttl: Time to live in seconds, None for default
            
        Returns:
            bool: Success of setting the cache
        """
        if ttl is None:
            ttl = self.ttl_default
        
        cache_key = self._make_cache_key(key, namespace)
        expires_at = time.time() + ttl
        
        # Store in memory cache
        self.memory_cache[cache_key] = {
            'value': value,
            'expires_at': expires_at,
            'last_accessed': time.time()
        }
        
        # If S3 enabled, also store there for persistence
        if self.use_s3:
            try:
                s3_key = f"{self.s3_prefix}{namespace}/{cache_key}"
                
                # Convert to JSON string
                content = json.dumps(value)
                
                # Set metadata
                metadata = {
                    'expires-at': str(expires_at),
                    'last-accessed': str(time.time()),
                    'namespace': namespace
                }
                
                # Upload to S3
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=s3_key,
                    Body=content,
                    ContentType='application/json',
                    Metadata=metadata
                )
                
                self.logger.debug(f"Stored in S3 cache: {namespace}/{key}")
            except Exception as e:
                self.logger.error(f"Error storing in S3 cache: {str(e)}")
                return False
        
        self.logger.debug(f"Cached {namespace}/{key} for {ttl} seconds")
        return True
    
    def invalidate(self, key: str, namespace: str = 'default') -> bool:
        """
        Invalidate a specific cache entry.
        
        Args:
            key: The cache key
            namespace: The namespace for the key
            
        Returns:
            bool: Success of invalidating the cache
        """
        cache_key = self._make_cache_key(key, namespace)
        
        # Remove from memory cache
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        
        # Remove from S3 if enabled
        if self.use_s3:
            try:
                s3_key = f"{self.s3_prefix}{namespace}/{cache_key}"
                self.s3_client.delete_object(Bucket=self.s3_bucket, Key=s3_key)
                self.logger.debug(f"Invalidated S3 cache for {namespace}/{key}")
            except Exception as e:
                self.logger.error(f"Error invalidating S3 cache: {str(e)}")
                return False
        
        self.logger.debug(f"Invalidated cache for {namespace}/{key}")
        return True
    
    def invalidate_namespace(self, namespace: str) -> bool:
        """
        Invalidate all cache entries in a namespace.
        
        Args:
            namespace: The namespace to invalidate
            
        Returns:
            bool: Success of invalidating the namespace
        """
        # Remove from memory cache
        keys_to_delete = []
        for cache_key in self.memory_cache:
            if cache_key.startswith(f"{namespace}:"):
                keys_to_delete.append(cache_key)
        
        for key in keys_to_delete:
            del self.memory_cache[key]
        
        # Remove from S3 if enabled
        if self.use_s3:
            try:
                # List objects with prefix
                s3_prefix = f"{self.s3_prefix}{namespace}/"
                paginator = self.s3_client.get_paginator('list_objects_v2')
                
                # Delete all objects with prefix
                for page in paginator.paginate(Bucket=self.s3_bucket, Prefix=s3_prefix):
                    if 'Contents' in page:
                        delete_keys = {'Objects': [{'Key': obj['Key']} for obj in page['Contents']]}
                        self.s3_client.delete_objects(Bucket=self.s3_bucket, Delete=delete_keys)
                
                self.logger.debug(f"Invalidated S3 cache for namespace {namespace}")
            except Exception as e:
                self.logger.error(f"Error invalidating S3 cache namespace: {str(e)}")
                return False
        
        self.logger.debug(f"Invalidated cache for namespace {namespace}")
        return True
    
    def cleanup(self) -> None:
        """
        Clean up expired items from memory cache.
        This is called periodically to prevent memory leaks.
        """
        current_time = time.time()
        keys_to_delete = []
        
        for cache_key, cache_item in self.memory_cache.items():
            if current_time > cache_item.get('expires_at', 0):
                keys_to_delete.append(cache_key)
        
        for key in keys_to_delete:
            del self.memory_cache[key]
        
        if keys_to_delete:
            self.logger.debug(f"Cleaned up {len(keys_to_delete)} expired cache items")
    
    def _make_cache_key(self, key: str, namespace: str) -> str:
        """Create a unique cache key."""
        # Simple concatenation for memory cache
        return f"{namespace}:{hashlib.md5(key.encode()).hexdigest()}"
    
    def _update_s3_metadata(self, s3_key: str, metadata_updates: Dict[str, str]) -> bool:
        """Update metadata for an S3 object without copying the object."""
        try:
            # Get current object metadata
            response = self.s3_client.head_object(Bucket=self.s3_bucket, Key=s3_key)
            current_metadata = response.get('Metadata', {})
            
            # Merge with updates
            new_metadata = {**current_metadata, **metadata_updates}
            
            # Copy object to itself with new metadata
            self.s3_client.copy_object(
                Bucket=self.s3_bucket,
                CopySource={'Bucket': self.s3_bucket, 'Key': s3_key},
                Key=s3_key,
                Metadata=new_metadata,
                MetadataDirective='REPLACE'
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating S3 metadata: {str(e)}")
            return False
    
    def get_adaptive_ttl(self, key: str, namespace: str, base_ttl: int = 300) -> int:
        """
        Calculate adaptive TTL based on access frequency.
        More frequently accessed items get longer TTLs.
        
        Args:
            key: The cache key
            namespace: The namespace
            base_ttl: Base TTL to start from
            
        Returns:
            Calculated TTL in seconds
        """
        cache_key = self._make_cache_key(key, namespace)
        
        if cache_key in self.memory_cache:
            # If item exists, check access frequency
            last_accessed = self.memory_cache[cache_key].get('last_accessed', 0)
            time_since_access = time.time() - last_accessed
            
            if time_since_access < 60:  # Accessed within last minute
                # Frequently accessed item, increase TTL
                return base_ttl * 2
            elif time_since_access < 300:  # Accessed within last 5 minutes
                # Moderately accessed, use normal TTL
                return base_ttl
            else:
                # Rarely accessed, decrease TTL
                return max(60, base_ttl // 2)
        
        # Default for new items
        return base_ttl