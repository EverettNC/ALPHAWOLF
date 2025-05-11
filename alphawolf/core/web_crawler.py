###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# WEB CRAWLER
# Automated content collection system that retrieves and processes information
# from authorized sources to maintain up-to-date knowledge for both users and the system.
###############################################################################

import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class WebCrawler:
    """
    Web Crawler - Content collection and processing system
    
    Retrieves information from authorized sources about dementia, Alzheimer's,
    and related topics to keep the knowledge base current and relevant.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Web Crawler.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.sources = []
        self.crawl_history = {}
        self.content_cache = {}
        
        # Load configuration
        self._load_config(config_path)
        
        logger.info("Web Crawler initialized")
    
    def _load_config(self, config_path: Optional[str] = None):
        """
        Load crawler configuration.
        
        Args:
            config_path: Optional path to configuration file
        """
        try:
            # Default config path if none provided
            if config_path is None:
                config_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'data',
                    'crawler_config.json'
                )
            
            # Check if config file exists
            if not os.path.exists(config_path):
                logger.warning(f"No configuration file found at {config_path}. Using default sources.")
                self._set_default_sources()
                return
            
            # Load config
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Set sources from config
            self.sources = config.get('sources', [])
            
            # Load crawl history if available
            history_path = os.path.join(
                os.path.dirname(config_path),
                'crawler_history.json'
            )
            
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    self.crawl_history = json.load(f)
            
            logger.info(f"Loaded {len(self.sources)} sources from configuration")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self._set_default_sources()
    
    def _set_default_sources(self):
        """Set default sources for crawling."""
        self.sources = [
            {
                "name": "Alzheimer's Association",
                "url": "https://www.alz.org/",
                "type": "organization",
                "topics": ["alzheimer's", "dementia", "caregiving", "research"],
                "priority": 1,
                "frequency": "weekly"
            },
            {
                "name": "National Institute on Aging",
                "url": "https://www.nia.nih.gov/health/alzheimers",
                "type": "government",
                "topics": ["alzheimer's", "dementia", "aging", "research"],
                "priority": 1,
                "frequency": "weekly"
            },
            {
                "name": "Mayo Clinic - Dementia",
                "url": "https://www.mayoclinic.org/diseases-conditions/dementia/symptoms-causes/syc-20352013",
                "type": "medical",
                "topics": ["dementia", "symptoms", "treatment", "prevention"],
                "priority": 2,
                "frequency": "monthly"
            },
            {
                "name": "Dementia Society of America",
                "url": "https://www.dementiasociety.org/",
                "type": "organization",
                "topics": ["dementia", "support", "caregiving", "education"],
                "priority": 2,
                "frequency": "monthly"
            },
            {
                "name": "AARP - Caregiving",
                "url": "https://www.aarp.org/caregiving/",
                "type": "organization",
                "topics": ["caregiving", "aging", "family care", "resources"],
                "priority": 3,
                "frequency": "monthly"
            }
        ]
    
    def crawl(self, topic: Optional[str] = None, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Crawl sources for content.
        
        Args:
            topic: Optional topic filter
            force_refresh: Force refresh regardless of last crawl time
            
        Returns:
            Dict with crawl results
        """
        start_time = time.time()
        results = {
            'sources_processed': 0,
            'new_content': 0,
            'updated_content': 0,
            'errors': 0,
            'topics': set(),
            'content': []
        }
        
        # Filter sources by topic if specified
        sources_to_crawl = self.sources
        if topic:
            sources_to_crawl = [s for s in self.sources if topic.lower() in [t.lower() for t in s.get('topics', [])]]
        
        logger.info(f"Beginning crawl of {len(sources_to_crawl)} sources" + (f" for topic '{topic}'" if topic else ""))
        
        # Process each source
        for source in sources_to_crawl:
            source_name = source.get('name', 'Unknown')
            source_url = source.get('url', '')
            
            if not source_url:
                logger.warning(f"Skipping source '{source_name}' with no URL")
                continue
            
            # Check if we need to refresh this source
            if not force_refresh and not self._should_refresh(source):
                logger.info(f"Skipping source '{source_name}' - recently crawled")
                continue
            
            logger.info(f"Crawling source: {source_name} ({source_url})")
            
            try:
                # In a production system, this would use a proper web crawler
                # For this demo, we'll simulate the crawl process
                content = self._simulate_crawl(source)
                
                # Process and store the content
                content_hash = hashlib.md5(json.dumps(content).encode()).hexdigest()
                source_id = hashlib.md5(source_url.encode()).hexdigest()
                
                # Check if content is new or updated
                is_new = source_id not in self.content_cache
                is_updated = not is_new and self.content_cache.get(source_id, {}).get('hash') != content_hash
                
                # Store in cache
                self.content_cache[source_id] = {
                    'hash': content_hash,
                    'content': content,
                    'last_updated': datetime.utcnow().isoformat() + "Z"
                }
                
                # Update crawl history
                self.crawl_history[source_id] = {
                    'last_crawl': datetime.utcnow().isoformat() + "Z",
                    'success': True,
                    'source_name': source_name,
                    'source_url': source_url
                }
                
                # Update results
                results['sources_processed'] += 1
                if is_new:
                    results['new_content'] += 1
                elif is_updated:
                    results['updated_content'] += 1
                
                for topic in source.get('topics', []):
                    results['topics'].add(topic)
                
                # Add content to results
                results['content'].append({
                    'source_name': source_name,
                    'source_url': source_url,
                    'timestamp': datetime.utcnow().isoformat() + "Z",
                    'topics': source.get('topics', []),
                    'is_new': is_new,
                    'is_updated': is_updated,
                    'content': content
                })
                
            except Exception as e:
                logger.error(f"Error crawling source '{source_name}': {str(e)}")
                results['errors'] += 1
                
                # Update crawl history with error
                source_id = hashlib.md5(source_url.encode()).hexdigest()
                self.crawl_history[source_id] = {
                    'last_crawl': datetime.utcnow().isoformat() + "Z",
                    'success': False,
                    'error': str(e),
                    'source_name': source_name,
                    'source_url': source_url
                }
        
        # Convert topics set to list for JSON serialization
        results['topics'] = list(results['topics'])
        
        # Calculate duration
        duration = time.time() - start_time
        results['duration_seconds'] = duration
        
        logger.info(f"Crawl completed in {duration:.2f}s: {results['sources_processed']} sources, "
                   f"{results['new_content']} new, {results['updated_content']} updated, "
                   f"{results['errors']} errors")
        
        # Save crawl history
        self._save_history()
        
        return results
    
    def _should_refresh(self, source: Dict[str, Any]) -> bool:
        """
        Determine if a source should be refreshed based on frequency and last crawl time.
        
        Args:
            source: Source configuration
            
        Returns:
            True if the source should be refreshed
        """
        source_url = source.get('url', '')
        if not source_url:
            return False
        
        # Get source ID
        source_id = hashlib.md5(source_url.encode()).hexdigest()
        
        # If no crawl history, definitely refresh
        if source_id not in self.crawl_history:
            return True
        
        # Get last crawl time
        last_crawl_str = self.crawl_history[source_id].get('last_crawl')
        if not last_crawl_str:
            return True
        
        try:
            # Parse last crawl time
            last_crawl = datetime.fromisoformat(last_crawl_str.rstrip('Z'))
            
            # Get current time
            now = datetime.utcnow()
            
            # Calculate time since last crawl
            time_since_crawl = (now - last_crawl).total_seconds()
            
            # Determine refresh frequency in seconds
            frequency = source.get('frequency', 'weekly')
            
            if frequency == 'hourly':
                refresh_seconds = 3600
            elif frequency == 'daily':
                refresh_seconds = 86400
            elif frequency == 'weekly':
                refresh_seconds = 604800
            elif frequency == 'monthly':
                refresh_seconds = 2592000
            else:
                refresh_seconds = 604800  # Default to weekly
            
            # Consider source priority (higher priority = more frequent)
            priority = source.get('priority', 2)
            refresh_seconds = int(refresh_seconds / priority)
            
            # Return whether it's time to refresh
            return time_since_crawl >= refresh_seconds
            
        except Exception as e:
            logger.error(f"Error checking refresh time: {str(e)}")
            return True  # Default to refresh on error
    
    def _simulate_crawl(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate crawling a source for content.
        In a production system, this would use a proper web crawler.
        
        Args:
            source: Source configuration
            
        Returns:
            Dict with crawled content
        """
        # In a real system, this would fetch and process real web content
        # For this demo, we'll return simulated content
        
        source_type = source.get('type', 'unknown')
        topics = source.get('topics', [])
        source_name = source.get('name', 'Unknown')
        
        # Sample article templates by source type
        templates = {
            'organization': [
                {
                    'title': 'Understanding {topic} for Families and Caregivers',
                    'content': 'This comprehensive guide helps families understand {topic} and provides practical tips for daily care.',
                    'tags': ['guide', 'family', 'tips']
                },
                {
                    'title': 'New Research on {topic} Treatment Options',
                    'content': 'Recent studies have shown promising results for {topic} treatments focusing on early intervention.',
                    'tags': ['research', 'treatment', 'innovation']
                }
            ],
            'government': [
                {
                    'title': 'National Guidelines for {topic} Management',
                    'content': 'The latest health guidelines recommend an integrated approach to {topic} care including medication, therapy, and lifestyle modifications.',
                    'tags': ['guidelines', 'official', 'health policy']
                },
                {
                    'title': '{topic} Research Funding Opportunities',
                    'content': 'New grants available for researchers studying innovative approaches to {topic} care and treatment.',
                    'tags': ['funding', 'research', 'grants']
                }
            ],
            'medical': [
                {
                    'title': 'Clinical Trial Results: {topic} Intervention Study',
                    'content': 'A recent phase III trial showed significant improvement in {topic} symptoms with the new treatment approach.',
                    'tags': ['clinical', 'research', 'treatment']
                },
                {
                    'title': 'Diagnostic Advances in {topic}',
                    'content': 'New diagnostic techniques enable earlier and more accurate detection of {topic}, potentially improving treatment outcomes.',
                    'tags': ['diagnosis', 'technology', 'early detection']
                }
            ]
        }
        
        # Get templates for this source type, or use generic templates
        source_templates = templates.get(source_type, templates['organization'])
        
        # Generate simulated articles based on topics
        articles = []
        for topic in topics:
            # Pick a template 
            template = source_templates[hash(topic + source_name) % len(source_templates)]
            
            # Create an article from the template
            article = {
                'title': template['title'].replace('{topic}', topic.title()),
                'content': template['content'].replace('{topic}', topic),
                'topic': topic,
                'tags': template['tags'] + [topic],
                'publish_date': datetime.utcnow().isoformat() + "Z",
                'url': f"{source.get('url', 'https://example.com')}/{topic.replace(' ', '-')}"
            }
            
            articles.append(article)
        
        # Simulate content extraction with common elements
        return {
            'articles': articles,
            'source': source_name,
            'extracted_on': datetime.utcnow().isoformat() + "Z",
            'topics': topics,
            'article_count': len(articles)
        }
    
    def _save_history(self):
        """Save crawl history to file."""
        try:
            # Determine history path
            history_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'crawler_history.json'
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            
            # Save history
            with open(history_path, 'w') as f:
                json.dump(self.crawl_history, f, indent=2)
            
            logger.info(f"Saved crawl history for {len(self.crawl_history)} sources")
            
        except Exception as e:
            logger.error(f"Error saving crawl history: {str(e)}")
    
    def get_content_for_topic(self, topic: str, max_age_days: int = 30) -> List[Dict[str, Any]]:
        """
        Get cached content for a specific topic.
        
        Args:
            topic: Topic to retrieve content for
            max_age_days: Maximum age of content in days
            
        Returns:
            List of content items matching the topic
        """
        results = []
        max_age_seconds = max_age_days * 86400
        now = datetime.utcnow()
        
        for source_id, cache_item in self.content_cache.items():
            content = cache_item.get('content', {})
            last_updated_str = cache_item.get('last_updated')
            
            # Skip if no content or too old
            if not content or not last_updated_str:
                continue
            
            try:
                last_updated = datetime.fromisoformat(last_updated_str.rstrip('Z'))
                age_seconds = (now - last_updated).total_seconds()
                
                if age_seconds > max_age_seconds:
                    continue
                
                # Check if this content is for the requested topic
                source_topics = content.get('topics', [])
                if topic.lower() in [t.lower() for t in source_topics]:
                    results.append({
                        'source': content.get('source', 'Unknown'),
                        'articles': content.get('articles', []),
                        'last_updated': last_updated_str,
                        'age_days': int(age_seconds / 86400),
                        'source_id': source_id
                    })
            except Exception as e:
                logger.error(f"Error processing cached content: {str(e)}")
        
        return results
    
    def get_source_status(self) -> Dict[str, Any]:
        """
        Get status of all crawled sources.
        
        Returns:
            Dict with source status information
        """
        results = {
            'sources': [],
            'total_sources': len(self.sources),
            'crawled_sources': len(self.crawl_history),
            'total_content_items': sum(len(s.get('content', {}).get('articles', [])) 
                                      for s in self.content_cache.values())
        }
        
        # Add details for each source
        for source in self.sources:
            source_url = source.get('url', '')
            source_id = hashlib.md5(source_url.encode()).hexdigest() if source_url else None
            
            source_status = {
                'name': source.get('name', 'Unknown'),
                'url': source_url,
                'type': source.get('type', 'unknown'),
                'topics': source.get('topics', []),
                'priority': source.get('priority', 2),
                'frequency': source.get('frequency', 'weekly')
            }
            
            # Add crawl history if available
            if source_id and source_id in self.crawl_history:
                history = self.crawl_history[source_id]
                source_status.update({
                    'last_crawl': history.get('last_crawl', 'Never'),
                    'last_success': history.get('success', False),
                    'last_error': history.get('error') if not history.get('success', False) else None
                })
            else:
                source_status.update({
                    'last_crawl': 'Never',
                    'last_success': None,
                    'last_error': None
                })
            
            # Add cache status if available
            if source_id and source_id in self.content_cache:
                cache = self.content_cache[source_id]
                content = cache.get('content', {})
                source_status.update({
                    'last_updated': cache.get('last_updated', 'Never'),
                    'content_hash': cache.get('hash'),
                    'article_count': len(content.get('articles', []))
                })
            else:
                source_status.update({
                    'last_updated': 'Never',
                    'content_hash': None,
                    'article_count': 0
                })
            
            results['sources'].append(source_status)
        
        return results