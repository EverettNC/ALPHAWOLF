###############################################################################
# AlphaWolf - LumaCognify AI
# Part of The Christman AI Project
#
# WEB CRAWLER MODULE
# Automated content collection system that retrieves dementia and Alzheimer's
# related information from authorized sources to maintain up-to-date knowledge.
###############################################################################

import os
import logging
import json
import time
from datetime import datetime
import requests
from typing import Dict, List, Any, Optional
import trafilatura
import hashlib

logger = logging.getLogger("alphawolf.crawler")

class WebCrawler:
    """
    Web crawler for retrieving and processing dementia and Alzheimer's related content
    from authorized sources.
    """
    
    def __init__(self):
        """Initialize the crawler with configuration settings"""
        self.logger = logging.getLogger(__name__)
        
        # Set up storage directories
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.cache_dir = os.path.join(self.data_dir, 'cache')
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load source list
        self.sources_file = os.path.join(self.data_dir, 'sources.json')
        self.sources = self._load_sources()
        
        # Load existing articles
        self.articles_file = os.path.join(self.data_dir, 'articles.json')
        self.articles = self._load_articles()
        
        # Load existing tips
        self.tips_file = os.path.join(self.data_dir, 'tips.json')
        self.tips = self._load_tips()
        
        # Crawl rate limiting
        self.request_delay = 3  # seconds between requests to be respectful
        self.max_articles_per_run = 20
        
        self.logger.info("Web Crawler initialized")
    
    def _load_sources(self) -> List[Dict[str, Any]]:
        """Load the list of authorized sources to crawl"""
        if os.path.exists(self.sources_file):
            try:
                with open(self.sources_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading sources: {str(e)}")
                return self._create_default_sources()
        else:
            return self._create_default_sources()
    
    def _create_default_sources(self) -> List[Dict[str, Any]]:
        """Create a default list of authorized sources"""
        default_sources = [
            {
                "name": "Alzheimer's Association",
                "base_url": "https://www.alz.org",
                "feed_urls": ["https://www.alz.org/blog"],
                "article_patterns": ["/blog/", "/news/"],
                "category": "authority",
                "priority": 1
            },
            {
                "name": "National Institute on Aging",
                "base_url": "https://www.nia.nih.gov",
                "feed_urls": ["https://www.nia.nih.gov/news"],
                "article_patterns": ["/news/", "/health/alzheimers", "/health/dementia"],
                "category": "government",
                "priority": 1
            },
            {
                "name": "Dementia Society of America",
                "base_url": "https://www.dementiasociety.org",
                "feed_urls": ["https://www.dementiasociety.org/blog"],
                "article_patterns": ["/blog/", "/news/", "/article/"],
                "category": "nonprofit",
                "priority": 2
            },
            {
                "name": "Medical News Today - Alzheimer's",
                "base_url": "https://www.medicalnewstoday.com",
                "feed_urls": ["https://www.medicalnewstoday.com/categories/alzheimers"],
                "article_patterns": ["/articles/"],
                "category": "medical",
                "priority": 2
            }
        ]
        
        # Save the default sources
        try:
            with open(self.sources_file, 'w') as f:
                json.dump(default_sources, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving default sources: {str(e)}")
        
        return default_sources
    
    def _load_articles(self) -> List[Dict[str, Any]]:
        """Load existing articles from storage"""
        if os.path.exists(self.articles_file):
            try:
                with open(self.articles_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading articles: {str(e)}")
                return []
        return []
    
    def _load_tips(self) -> List[Dict[str, Any]]:
        """Load existing tips from storage"""
        if os.path.exists(self.tips_file):
            try:
                with open(self.tips_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading tips: {str(e)}")
                return []
        return []
    
    def _save_articles(self) -> bool:
        """Save articles to storage"""
        try:
            with open(self.articles_file, 'w') as f:
                json.dump(self.articles, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving articles: {str(e)}")
            return False
    
    def _save_tips(self) -> bool:
        """Save tips to storage"""
        try:
            with open(self.tips_file, 'w') as f:
                json.dump(self.tips, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving tips: {str(e)}")
            return False
    
    def get_website_text_content(self, url: str) -> str:
        """
        Extract the main text content from a webpage using trafilatura.
        
        Args:
            url: URL of the webpage to extract content from
            
        Returns:
            Extracted text content
        """
        try:
            # Generate cache key
            url_hash = hashlib.md5(url.encode()).hexdigest()
            cache_file = os.path.join(self.cache_dir, f"{url_hash}.txt")
            
            # Check cache first
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Download and extract content
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                self.logger.warning(f"Failed to download content from {url}")
                return ""
                
            text = trafilatura.extract(downloaded)
            if not text:
                self.logger.warning(f"Failed to extract text from {url}")
                return ""
            
            # Cache the result
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(text)
            except Exception as e:
                self.logger.error(f"Error caching content: {str(e)}")
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {str(e)}")
            return ""
    
    def _extract_article_urls(self, feed_url: str, article_patterns: List[str]) -> List[str]:
        """
        Extract article URLs from a feed page.
        
        Args:
            feed_url: URL of the feed page
            article_patterns: List of URL patterns that indicate article pages
            
        Returns:
            List of article URLs
        """
        try:
            response = requests.get(feed_url, timeout=10)
            if response.status_code != 200:
                self.logger.warning(f"Failed to fetch feed {feed_url}: {response.status_code}")
                return []
            
            # Extract all links from the page
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            all_links = soup.find_all('a', href=True)
            
            article_urls = []
            base_url = '/'.join(feed_url.split('/')[:3])  # Extract the base URL (scheme + domain)
            
            # Filter links that match article patterns
            for link in all_links:
                href = link['href']
                
                # Handle relative URLs
                if href.startswith('/'):
                    href = base_url + href
                elif not href.startswith(('http://', 'https://')):
                    continue
                
                # Check if link matches any article pattern
                if any(pattern in href for pattern in article_patterns):
                    if href not in article_urls:
                        article_urls.append(href)
            
            return article_urls
            
        except Exception as e:
            self.logger.error(f"Error extracting article URLs from {feed_url}: {str(e)}")
            return []
    
    def _process_article(self, url: str, source_name: str) -> Optional[Dict[str, Any]]:
        """
        Process an article URL to extract content and metadata.
        
        Args:
            url: URL of the article
            source_name: Name of the source
            
        Returns:
            Dictionary with article data or None if processing failed
        """
        try:
            # Check if already processed
            if any(article['url'] == url for article in self.articles):
                return None
            
            # Extract content
            content = self.get_website_text_content(url)
            if not content or len(content) < 500:  # Minimum content length
                return None
            
            # Extract title (first line or first sentence)
            title = content.strip().split('\n')[0].strip()
            if len(title) > 100:
                title = title[:97] + '...'
            
            # Generate summary using first paragraph
            paragraphs = [p for p in content.split('\n') if p.strip()]
            summary = paragraphs[1] if len(paragraphs) > 1 else paragraphs[0]
            if len(summary) > 200:
                summary = summary[:197] + '...'
            
            # Create article object
            article = {
                'id': hashlib.md5(url.encode()).hexdigest(),
                'url': url,
                'title': title,
                'summary': summary,
                'content': content,
                'source': source_name,
                'published_date': datetime.now().isoformat(),  # Actual date would be extracted from the article
                'crawled_date': datetime.now().isoformat(),
                'keywords': self._extract_keywords(content),
                'category': 'research'  # Default category
            }
            
            return article
            
        except Exception as e:
            self.logger.error(f"Error processing article {url}: {str(e)}")
            return None
    
    def _extract_keywords(self, content: str) -> List[str]:
        """
        Extract relevant keywords from article content.
        
        Args:
            content: Article content text
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction based on frequency
        # In a real implementation, this would use NLP techniques
        keywords = []
        
        # List of relevant terms to look for
        dementia_terms = [
            "alzheimer", "dementia", "cognitive decline", "memory loss", "brain health",
            "neurodegeneration", "mild cognitive impairment", "caregiver", "neurology",
            "amyloid", "tau protein", "hippocampus", "brain scan", "clinical trial"
        ]
        
        for term in dementia_terms:
            if term.lower() in content.lower():
                keywords.append(term)
        
        return keywords[:10]  # Limit to 10 keywords
    
    def _extract_tips(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract helpful tips from articles.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of tip dictionaries
        """
        tips = []
        
        for article in articles:
            content = article['content']
            
            # Look for paragraphs that might contain tips
            paragraphs = content.split('\n')
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                # Look for indicators of tips
                tip_indicators = ["tip", "advice", "recommend", "suggestion", "helpful", "should", "try"]
                if any(indicator in paragraph.lower() for indicator in tip_indicators) and 20 < len(paragraph) < 200:
                    # Create tip object
                    tip = {
                        'id': hashlib.md5(paragraph.encode()).hexdigest(),
                        'text': paragraph,
                        'source': article['source'],
                        'source_url': article['url'],
                        'category': self._categorize_tip(paragraph),
                        'added_date': datetime.now().isoformat()
                    }
                    
                    # Check for duplicates
                    if not any(existing['text'] == tip['text'] for existing in self.tips):
                        tips.append(tip)
        
        return tips
    
    def _categorize_tip(self, text: str) -> str:
        """
        Categorize a tip based on its content.
        
        Args:
            text: Tip text
            
        Returns:
            Category name
        """
        categories = {
            'caregiving': ["caregiver", "caring", "help them", "assist", "support person"],
            'safety': ["safety", "secure", "prevent falls", "wandering", "safe"],
            'communication': ["communicat", "talk", "speak", "listen", "understand"],
            'activities': ["activit", "exercise", "game", "stimulation", "engagement"],
            'nutrition': ["food", "eat", "diet", "nutrition", "meal"],
            'medication': ["medicat", "pill", "drug", "prescription", "treatment"],
            'cognitive': ["memory", "brain", "cognitive", "mental", "thinking"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text.lower() for keyword in keywords):
                return category
        
        return "general"
    
    def run_scheduled_crawl(self) -> Dict[str, Any]:
        """
        Run a scheduled crawl to update articles and tips.
        
        Returns:
            Dictionary with crawl statistics
        """
        self.logger.info("Starting scheduled crawl")
        
        start_time = time.time()
        total_processed = 0
        new_articles = 0
        new_tips = 0
        
        # Process each source
        for source in sorted(self.sources, key=lambda s: s['priority']):
            self.logger.info(f"Processing source: {source['name']}")
            
            # Skip if max articles reached
            if new_articles >= self.max_articles_per_run:
                break
            
            # Process each feed URL
            for feed_url in source['feed_urls']:
                # Extract article URLs
                article_urls = self._extract_article_urls(feed_url, source['article_patterns'])
                self.logger.info(f"Found {len(article_urls)} article URLs from {feed_url}")
                
                # Process each article URL
                for url in article_urls:
                    # Skip if max articles reached
                    if new_articles >= self.max_articles_per_run:
                        break
                    
                    # Process article
                    article = self._process_article(url, source['name'])
                    if article:
                        self.articles.append(article)
                        new_articles += 1
                    
                    total_processed += 1
                    
                    # Apply rate limiting
                    time.sleep(self.request_delay)
        
        # Extract tips from new articles
        if new_articles > 0:
            # Only process the newly added articles
            new_article_objects = self.articles[-new_articles:]
            new_tips_list = self._extract_tips(new_article_objects)
            
            # Add new tips
            for tip in new_tips_list:
                if not any(existing['id'] == tip['id'] for existing in self.tips):
                    self.tips.append(tip)
                    new_tips += 1
        
        # Save updated data
        self._save_articles()
        self._save_tips()
        
        elapsed_time = time.time() - start_time
        
        # Log summary
        self.logger.info(f"Crawl completed in {elapsed_time:.2f} seconds")
        self.logger.info(f"Processed {total_processed} URLs")
        self.logger.info(f"Added {new_articles} new articles")
        self.logger.info(f"Added {new_tips} new tips")
        
        return {
            "elapsed_time": elapsed_time,
            "urls_processed": total_processed,
            "articles_count": new_articles,
            "tips_count": new_tips,
            "timestamp": datetime.now().isoformat()
        }
    
# For standalone testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    crawler = WebCrawler()
    result = crawler.run_scheduled_crawl()
    print(json.dumps(result, indent=2))