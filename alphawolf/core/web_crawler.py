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
"""
AlphaWolf Web Crawler
Part of The Christman AI Project - LumaCognify AI

This module provides web crawling capabilities for retrieving authoritative
information about Alzheimer's and dementia from trusted sources.

"HOW CAN I HELP YOU LOVE YOURSELF MORE"
"""

import os
import logging
import datetime
import hashlib
import json
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, urljoin

try:
    import trafilatura
    from trafilatura.settings import use_config
    from trafilatura import fetch_url
except ImportError:
    # Define placeholder if trafilatura is not available
    def fetch_url(url):
        return None
        
    def extract(html):
        return "Content extraction not available"

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_USER_AGENT = "AlphaWolf-ResearchBot/1.0 (LumaCognify AI; research@lumacognify.ai; +https://alphawolf.christmanai.org/bot.html)"
AUTHORITATIVE_DOMAINS = [
    # Health organizations
    "nih.gov", "alz.org", "alzheimers.org.uk", "who.int", "cdc.gov", "alzforum.org",
    "dementia.org", "nia.nih.gov", "alzheimers.gov", "alzheimersresearchuk.org",
    # Academic institutions
    "edu", "ac.uk", "harvard.edu", "stanford.edu", "mayo.edu", "hopkinsmedicine.org",
    "ucl.ac.uk", "oxfordhealth.nhs.uk", "thelancet.com", "nejm.org", "jamanetwork.com",
    # Reputable health websites
    "mayoclinic.org", "webmd.com", "clevelandclinic.org", "hopkinsmedicine.org", 
    "medlineplus.gov", "healthline.com", "medicalnewstoday.com"
]

# Crawler configuration
DEFAULT_CONFIG = {
    "max_depth": 3,
    "pages_per_source": 10,
    "crawl_delay": 2.0,  # Seconds between requests to same domain
    "timeout": 30,
    "max_content_length": 500000,  # ~500KB
    "respect_robots": True,
    "only_authoritative": True,
    "cache_days": 7  # Cache retrieved content for this many days
}

class WebCrawler:
    """
    AlphaWolf web crawler for retrieving information from authoritative sources
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, cache_dir: Optional[str] = None):
        """
        Initialize the web crawler
        
        Parameters:
        - config: Optional configuration dictionary
        - cache_dir: Directory to store cached content
        """
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "..", "data", "crawler_cache")
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Domain-specific crawl delays to avoid overloading servers
        self.domain_access_times = {}
        
        # Generate a unique instance ID for logging
        instance_hash = hashlib.md5(str(datetime.datetime.utcnow().timestamp()).encode()).hexdigest()[:8]
        self.instance_id = f"web_crawler_{instance_hash}"
        
        # Initialize trafilatura config if available
        try:
            self.trafilatura_config = use_config()
            self.trafilatura_config.set("DEFAULT", "USER_AGENT", DEFAULT_USER_AGENT)
        except (NameError, AttributeError):
            self.trafilatura_config = None
            
        logger.info(f"WebCrawler initialized with ID {self.instance_id}")
        
    def search_topic(self, 
                    topic: str, 
                    subtopics: Optional[List[str]] = None, 
                    max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for information on a specific topic
        
        Parameters:
        - topic: The main topic to search for
        - subtopics: Optional list of subtopics to narrow the search
        - max_results: Maximum number of results to return
        
        Returns:
        - List of information items with metadata
        """
        results = []
        search_terms = [topic]
        
        if subtopics:
            search_terms.extend([f"{topic} {subtopic}" for subtopic in subtopics])
            
        logger.info(f"Searching for topics: {search_terms}")
        
        # Start URLs for major authoritative sources
        start_urls = [
            f"https://www.alz.org/search?searchtext={topic.replace(' ', '+')}",
            f"https://www.nia.nih.gov/search?search={topic.replace(' ', '+')}",
            f"https://www.alzheimers.gov/search?query={topic.replace(' ', '+')}",
            f"https://www.mayoclinic.org/search/search-results?q={topic.replace(' ', '+')}"
        ]
        
        # Process each start URL
        for url in start_urls:
            if len(results) >= max_results:
                break
                
            try:
                domain = urlparse(url).netloc
                
                # Respect crawl delay
                self._respect_crawl_delay(domain)
                
                # Try to get from cache first
                cached_content = self._get_from_cache(url)
                if cached_content:
                    logger.info(f"Using cached content for {url}")
                    links = self._extract_links(cached_content, url)
                else:
                    # Fetch the search results page
                    logger.info(f"Fetching search results from {url}")
                    html = fetch_url(url, config=self.trafilatura_config)
                    
                    if not html:
                        logger.warning(f"Failed to fetch {url}")
                        continue
                        
                    # Extract links from search results
                    links = self._extract_links(html, url)
                    
                    # Save to cache
                    self._save_to_cache(url, html)
                
                # Process each link
                for link in links[:self.config["pages_per_source"]]:
                    if len(results) >= max_results:
                        break
                        
                    try:
                        # Respect crawl delay
                        link_domain = urlparse(link).netloc
                        self._respect_crawl_delay(link_domain)
                        
                        # Only process authoritative domains if configured
                        if self.config["only_authoritative"] and not self._is_authoritative(link_domain):
                            logger.info(f"Skipping non-authoritative domain: {link_domain}")
                            continue
                        
                        # Try to get from cache first
                        content_info = self._get_content_from_cache(link)
                        
                        if not content_info:
                            # Fetch and extract content
                            logger.info(f"Fetching content from {link}")
                            html = fetch_url(link, config=self.trafilatura_config)
                            
                            if not html:
                                logger.warning(f"Failed to fetch {link}")
                                continue
                                
                            # Extract main content
                            content = trafilatura.extract(html, include_comments=False, include_tables=True)
                            
                            if not content or len(content.strip()) < 100:
                                logger.warning(f"No significant content extracted from {link}")
                                continue
                                
                            # Extract metadata
                            metadata = trafilatura.metadata.extract_metadata(html, url=link)
                            
                            # Create content info
                            content_info = {
                                "url": link,
                                "title": metadata.title if metadata else self._extract_title(html),
                                "authors": metadata.author if metadata else None,
                                "date": metadata.date if metadata else None,
                                "content": content,
                                "source": link_domain,
                                "retrieved": datetime.datetime.utcnow().isoformat()
                            }
                            
                            # Save to cache
                            self._save_content_to_cache(link, content_info)
                            
                        # Add to results
                        results.append(content_info)
                        
                    except Exception as e:
                        logger.error(f"Error processing link {link}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error processing start URL {url}: {e}")
                continue
                
        # Add search metadata
        for result in results:
            result["topic"] = topic
            result["relevance_score"] = self._calculate_relevance(result["content"], topic, subtopics)
            
        # Sort by relevance
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        logger.info(f"Retrieved {len(results)} results for topic '{topic}'")
        return results[:max_results]
    
    def get_latest_research(self, 
                           condition: str, 
                           max_results: int = 5, 
                           max_age_days: int = 90) -> List[Dict[str, Any]]:
        """
        Get latest research on a specific condition
        
        Parameters:
        - condition: The medical condition to search for (e.g., "Alzheimer's")
        - max_results: Maximum number of results to return
        - max_age_days: Maximum age of research in days
        
        Returns:
        - List of research papers/articles with metadata
        """
        results = []
        
        # Research-specific sources
        research_urls = [
            f"https://pubmed.ncbi.nlm.nih.gov/?term={condition.replace(' ', '+')}",
            f"https://alzforum.org/search?term={condition.replace(' ', '+')}",
            f"https://www.alzheimersresearchuk.org/search?term={condition.replace(' ', '+')}"
        ]
        
        # Process each research URL
        for url in research_urls:
            if len(results) >= max_results:
                break
                
            try:
                domain = urlparse(url).netloc
                
                # Respect crawl delay
                self._respect_crawl_delay(domain)
                
                # Try to get from cache first
                cached_content = self._get_from_cache(url)
                if cached_content:
                    logger.info(f"Using cached content for {url}")
                    links = self._extract_links(cached_content, url)
                else:
                    # Fetch the search results page
                    logger.info(f"Fetching research results from {url}")
                    html = fetch_url(url, config=self.trafilatura_config)
                    
                    if not html:
                        logger.warning(f"Failed to fetch {url}")
                        continue
                        
                    # Extract links from search results
                    links = self._extract_links(html, url)
                    
                    # Save to cache
                    self._save_to_cache(url, html)
                
                # Process each link
                for link in links[:self.config["pages_per_source"]]:
                    if len(results) >= max_results:
                        break
                        
                    try:
                        # Respect crawl delay
                        link_domain = urlparse(link).netloc
                        self._respect_crawl_delay(link_domain)
                        
                        # Try to get from cache first
                        content_info = self._get_content_from_cache(link)
                        
                        if not content_info:
                            # Fetch and extract content
                            logger.info(f"Fetching research from {link}")
                            html = fetch_url(link, config=self.trafilatura_config)
                            
                            if not html:
                                logger.warning(f"Failed to fetch {link}")
                                continue
                                
                            # Extract main content
                            content = trafilatura.extract(html, include_comments=False, include_tables=True)
                            
                            if not content or len(content.strip()) < 100:
                                logger.warning(f"No significant content extracted from {link}")
                                continue
                                
                            # Extract metadata
                            metadata = trafilatura.metadata.extract_metadata(html, url=link)
                            
                            # Create content info
                            content_info = {
                                "url": link,
                                "title": metadata.title if metadata else self._extract_title(html),
                                "authors": metadata.author if metadata else None,
                                "date": metadata.date if metadata else None,
                                "content": content,
                                "source": link_domain,
                                "retrieved": datetime.datetime.utcnow().isoformat(),
                                "is_research": True
                            }
                            
                            # Save to cache
                            self._save_content_to_cache(link, content_info)
                            
                        # Check if research is recent enough
                        if content_info.get("date"):
                            try:
                                pub_date = datetime.datetime.fromisoformat(content_info["date"].replace('Z', '+00:00'))
                                age_days = (datetime.datetime.utcnow() - pub_date).days
                                
                                if age_days > max_age_days:
                                    logger.info(f"Skipping older research: {content_info.get('title')} ({age_days} days old)")
                                    continue
                            except (ValueError, TypeError):
                                # If date can't be parsed, include it anyway
                                pass
                        
                        # Add to results
                        content_info["condition"] = condition
                        content_info["relevance_score"] = self._calculate_relevance(content_info["content"], condition)
                        results.append(content_info)
                        
                    except Exception as e:
                        logger.error(f"Error processing research link {link}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error processing research URL {url}: {e}")
                continue
                
        # Sort by date (newest first), then by relevance
        results.sort(key=lambda x: (x.get("date", ""), x.get("relevance_score", 0)), reverse=True)
        
        logger.info(f"Retrieved {len(results)} recent research items for condition '{condition}'")
        return results[:max_results]
    
    def extract_facts(self, 
                     content: Dict[str, Any], 
                     max_facts: int = 10) -> List[Dict[str, Any]]:
        """
        Extract factual information from content
        
        Parameters:
        - content: Content dictionary with text and metadata
        - max_facts: Maximum number of facts to extract
        
        Returns:
        - List of extracted facts with metadata
        """
        facts = []
        text = content.get("content", "")
        
        # Simple fact extraction based on paragraph breaks
        # In a real implementation, this would use ML or LLM to extract facts
        paragraphs = text.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            
            # Skip short paragraphs and those that don't have factual indicators
            if len(paragraph) < 30 or not self._looks_factual(paragraph):
                continue
                
            # Create fact entry
            fact = {
                "text": paragraph,
                "source_url": content.get("url"),
                "source_title": content.get("title"),
                "source_domain": content.get("source"),
                "extracted": datetime.datetime.utcnow().isoformat(),
                "confidence": self._assess_fact_confidence(paragraph, content.get("source", ""))
            }
            
            facts.append(fact)
            
            if len(facts) >= max_facts:
                break
                
        logger.info(f"Extracted {len(facts)} facts from content: {content.get('title')}")
        return facts
    
    def _respect_crawl_delay(self, domain: str) -> None:
        """
        Respect crawl delay for domains
        
        Parameters:
        - domain: The domain to check
        """
        now = time.time()
        
        if domain in self.domain_access_times:
            last_access_time = self.domain_access_times[domain]
            elapsed = now - last_access_time
            
            # Use default crawl delay
            delay = self.config["crawl_delay"]
            
            # Enforce minimum wait time
            if elapsed < delay:
                wait_time = delay - elapsed
                logger.debug(f"Waiting {wait_time:.2f}s for {domain}")
                time.sleep(wait_time)
                
        # Update access time
        self.domain_access_times[domain] = time.time()
        
    def _is_authoritative(self, domain: str) -> bool:
        """
        Check if a domain is authoritative
        
        Parameters:
        - domain: The domain to check
        
        Returns:
        - True if authoritative, False otherwise
        """
        return any(auth_domain in domain for auth_domain in AUTHORITATIVE_DOMAINS)
        
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract links from HTML
        
        Parameters:
        - html: The HTML content
        - base_url: The base URL for resolving relative links
        
        Returns:
        - List of extracted links
        """
        links = []
        
        # Simple regex-based link extraction
        # In a real implementation, use a proper HTML parser
        href_pattern = re.compile(r'href=["\'](.*?)["\']')
        matches = href_pattern.findall(html)
        
        for match in matches:
            try:
                # Resolve relative URLs
                absolute_url = urljoin(base_url, match)
                
                # Skip non-HTTP URLs
                if not absolute_url.startswith(('http://', 'https://')):
                    continue
                    
                # Skip URLs with fragments
                if '#' in absolute_url:
                    absolute_url = absolute_url.split('#')[0]
                    
                # Skip URLs with query parameters (simplified)
                if '?' in absolute_url:
                    absolute_url = absolute_url.split('?')[0]
                    
                # Skip duplicate links
                if absolute_url not in links:
                    links.append(absolute_url)
            except Exception:
                continue
                
        return links
        
    def _extract_title(self, html: str) -> str:
        """
        Extract title from HTML
        
        Parameters:
        - html: The HTML content
        
        Returns:
        - Extracted title or "Unknown Title"
        """
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        
        if title_match:
            return title_match.group(1).strip()
        
        return "Unknown Title"
        
    def _calculate_relevance(self, 
                            content: str, 
                            topic: str, 
                            subtopics: Optional[List[str]] = None) -> float:
        """
        Calculate relevance score of content to topic
        
        Parameters:
        - content: The content text
        - topic: The main topic
        - subtopics: Optional list of subtopics
        
        Returns:
        - Relevance score from 0.0 to 1.0
        """
        if not content:
            return 0.0
            
        content_lower = content.lower()
        topic_lower = topic.lower()
        
        # Basic relevance based on keyword frequency
        topic_count = content_lower.count(topic_lower)
        
        # Normalize by content length
        content_length = len(content_lower)
        base_score = min(1.0, (topic_count * 1000) / content_length)
        
        # Add subtopic relevance
        if subtopics:
            subtopic_score = 0.0
            
            for subtopic in subtopics:
                subtopic_lower = subtopic.lower()
                subtopic_count = content_lower.count(subtopic_lower)
                subtopic_score += min(1.0, (subtopic_count * 500) / content_length)
                
            # Average the subtopic scores and combine with base score
            subtopic_score = subtopic_score / len(subtopics)
            final_score = (base_score * 0.7) + (subtopic_score * 0.3)
        else:
            final_score = base_score
            
        return round(final_score, 2)
        
    def _looks_factual(self, text: str) -> bool:
        """
        Check if text looks like a factual statement
        
        Parameters:
        - text: The text to check
        
        Returns:
        - True if likely factual, False otherwise
        """
        # Check length (facts are usually not too short or too long)
        if len(text) < 30 or len(text) > 500:
            return False
            
        # Check for factual indicators
        factual_patterns = [
            r'\b(?:is|are|was|were|has been|have been)\b',
            r'\b(?:percent|percentage|study|research|found|discovered)\b',
            r'\b(?:according to|research shows|evidence suggests)\b',
            r'\d+%',
            r'\d+ percent',
            r'\b(?:in \d+|patients|symptoms|treatment|diagnosis)\b'
        ]
        
        matches = 0
        for pattern in factual_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
                
        # If multiple factual patterns match, likely factual
        return matches >= 2
        
    def _assess_fact_confidence(self, fact_text: str, source_domain: str) -> float:
        """
        Assess confidence in a fact based on text and source
        
        Parameters:
        - fact_text: The fact text
        - source_domain: The source domain
        
        Returns:
        - Confidence score from 0.0 to 1.0
        """
        # Start with base confidence
        confidence = 0.5
        
        # Adjust based on source authority
        if self._is_authoritative(source_domain):
            # Higher base confidence for authoritative sources
            confidence += 0.2
            
        # Adjust based on text indicators
        
        # References to studies increase confidence
        if re.search(r'\b(?:study|research|trial|according to)\b', fact_text, re.IGNORECASE):
            confidence += 0.1
            
        # Statistical data increases confidence
        if re.search(r'\d+(?:\.\d+)?%|\d+ percent', fact_text, re.IGNORECASE):
            confidence += 0.1
            
        # Hedging language decreases confidence
        if re.search(r'\b(?:may|might|could|possibly|perhaps)\b', fact_text, re.IGNORECASE):
            confidence -= 0.1
            
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
        
    def _cache_path(self, url: str) -> str:
        """
        Generate cache file path for URL
        
        Parameters:
        - url: The URL to generate cache path for
        
        Returns:
        - Path to cache file
        """
        # Create URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        return os.path.join(self.cache_dir, f"{url_hash}.html")
        
    def _content_cache_path(self, url: str) -> str:
        """
        Generate content cache file path for URL
        
        Parameters:
        - url: The URL to generate cache path for
        
        Returns:
        - Path to content cache file
        """
        # Create URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        return os.path.join(self.cache_dir, f"{url_hash}.json")
        
    def _get_from_cache(self, url: str) -> Optional[str]:
        """
        Get HTML from cache if available and not expired
        
        Parameters:
        - url: The URL to retrieve from cache
        
        Returns:
        - Cached HTML or None if not available
        """
        cache_path = self._cache_path(url)
        
        if not os.path.exists(cache_path):
            return None
            
        # Check if cache is expired
        cache_time = os.path.getmtime(cache_path)
        cache_age_days = (time.time() - cache_time) / (24 * 3600)
        
        if cache_age_days > self.config["cache_days"]:
            logger.debug(f"Cache expired for {url}")
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading cache for {url}: {e}")
            return None
            
    def _save_to_cache(self, url: str, html: str) -> None:
        """
        Save HTML to cache
        
        Parameters:
        - url: The URL to cache
        - html: The HTML content to cache
        """
        cache_path = self._cache_path(url)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            logger.error(f"Error saving cache for {url}: {e}")
            
    def _get_content_from_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get content from cache if available and not expired
        
        Parameters:
        - url: The URL to retrieve from cache
        
        Returns:
        - Cached content or None if not available
        """
        cache_path = self._content_cache_path(url)
        
        if not os.path.exists(cache_path):
            return None
            
        # Check if cache is expired
        cache_time = os.path.getmtime(cache_path)
        cache_age_days = (time.time() - cache_time) / (24 * 3600)
        
        if cache_age_days > self.config["cache_days"]:
            logger.debug(f"Content cache expired for {url}")
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading content cache for {url}: {e}")
            return None
            
    def _save_content_to_cache(self, url: str, content: Dict[str, Any]) -> None:
        """
        Save content to cache
        
        Parameters:
        - url: The URL to cache
        - content: The content to cache
        """
        cache_path = self._content_cache_path(url)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving content cache for {url}: {e}")


# Create default instance
default_crawler = WebCrawler()

# Convenience functions
def search_topic(topic, subtopics=None, max_results=10):
    """Convenience function to search for information on a topic"""
    return default_crawler.search_topic(topic, subtopics, max_results)

def get_latest_research(condition, max_results=5, max_age_days=90):
    """Convenience function to get latest research on a condition"""
    return default_crawler.get_latest_research(condition, max_results, max_age_days)

def extract_facts(content, max_facts=10):
    """Convenience function to extract facts from content"""
    return default_crawler.extract_facts(content, max_facts)