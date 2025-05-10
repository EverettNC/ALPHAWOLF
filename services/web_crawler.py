import logging
import os
import json
import requests
import trafilatura
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

class WebCrawler:
    """Service for crawling web resources related to Alzheimer's and dementia research."""
    
    def __init__(self):
        """Initialize the web crawler service."""
        self.logger = logging.getLogger(__name__)
        self.data_dir = os.path.join('data')
        self.articles_file = os.path.join(self.data_dir, 'research_articles.json')
        self.tips_file = os.path.join(self.data_dir, 'daily_tips.json')
        self.resources_file = os.path.join(self.data_dir, 'resources.json')
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize trusted sources
        self.trusted_sources = [
            {
                'name': 'Alzheimer\'s Association',
                'url': 'https://www.alz.org',
                'article_selector': 'article',
                'category': 'research'
            },
            {
                'name': 'National Institute on Aging',
                'url': 'https://www.nia.nih.gov',
                'article_selector': '.field-items',
                'category': 'official'
            },
            {
                'name': 'Mayo Clinic',
                'url': 'https://www.mayoclinic.org',
                'article_selector': '.main-content',
                'category': 'medical'
            },
        ]
        
        self.logger.info("Web crawler service initialized")
    
    def crawl_sources(self, limit=5):
        """Crawl trusted sources for recent information."""
        self.logger.info(f"Starting crawl of {len(self.trusted_sources)} trusted sources")
        
        articles = []
        resources = {}
        tips = []
        
        for source in self.trusted_sources:
            try:
                self.logger.info(f"Crawling {source['name']} at {source['url']}")
                
                # Get the main page
                response = requests.get(source['url'], timeout=10)
                if response.status_code != 200:
                    self.logger.warning(f"Failed to access {source['url']}, status code: {response.status_code}")
                    continue
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract links to articles
                links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    # Convert relative URLs to absolute
                    if not href.startswith('http'):
                        href = urljoin(source['url'], href)
                    
                    # Only include links to the same domain
                    if urlparse(href).netloc == urlparse(source['url']).netloc:
                        # Filter for likely article pages
                        if any(keyword in href.lower() for keyword in ['/article/', '/news/', '/research/', '/blog/', '/story/']):
                            links.append(href)
                
                # Limit the number of links to process
                links = links[:limit]
                
                # Process each link
                for link in links:
                    try:
                        # Extract content using trafilatura
                        downloaded = trafilatura.fetch_url(link)
                        if not downloaded:
                            self.logger.warning(f"Failed to download content from {link}")
                            continue
                        
                        # Extract metadata and main content
                        extracted = trafilatura.extract(downloaded, output_format='json', include_links=True, 
                                                       include_images=True, include_tables=True)
                        
                        if not extracted:
                            self.logger.warning(f"No content extracted from {link}")
                            continue
                        
                        # Parse JSON
                        content = json.loads(extracted)
                        
                        # Create structured article
                        if 'title' in content and content['title']:
                            # Get current count of articles to use as ID
                            article_id = len(articles) + 1
                            
                            # Create article object
                            article = {
                                'id': article_id,
                                'title': content['title'],
                                'summary': content['description'] if 'description' in content else '',
                                'content': content['raw_text'] if 'raw_text' in content else '',
                                'date': content['date'] if 'date' in content else datetime.now().strftime('%Y-%m-%d'),
                                'source': source['name'],
                                'url': link,
                                'topics': self._extract_topics(content),
                                'image_url': self._extract_image(content, link),
                            }
                            
                            articles.append(article)
                            
                            # Extract tips if content seems appropriate
                            if len(content['raw_text']) < 1000 and ('tip' in link.lower() or 'advice' in link.lower()):
                                tip = {
                                    'id': len(tips) + 1,
                                    'title': content['title'],
                                    'content': content['raw_text'],
                                    'category': self._categorize_tip(content['title'], content['raw_text']),
                                    'date': datetime.now().strftime('%Y-%m-%d'),
                                    'source': source['name']
                                }
                                tips.append(tip)
                            
                            self.logger.info(f"Processed article: {content['title']}")
                        else:
                            self.logger.warning(f"No title found for content from {link}")
                    
                    except Exception as e:
                        self.logger.error(f"Error processing link {link}: {str(e)}")
            
            except Exception as e:
                self.logger.error(f"Error crawling source {source['name']}: {str(e)}")
        
        # Save crawled data
        if articles:
            self._save_articles(articles)
        
        if tips:
            self._save_tips(tips)
        
        return {
            'articles_count': len(articles),
            'tips_count': len(tips)
        }
    
    def _extract_topics(self, content):
        """Extract likely topics from content."""
        topics = []
        
        # List of possible topics
        possible_topics = [
            'Research', 'Prevention', 'Diagnosis', 'Treatment', 'Care', 
            'Nutrition', 'Exercise', 'Sleep', 'Memory', 'Communication',
            'Behavior', 'Medication', 'Therapy', 'Caregiving', 'Safety',
            'Technology', 'Lifestyle'
        ]
        
        # Check title and content for topics
        text = content['title'] + ' ' + content['raw_text']
        for topic in possible_topics:
            if topic.lower() in text.lower():
                topics.append(topic)
        
        # Ensure at least one topic
        if not topics:
            topics = ['General']
        
        return topics
    
    def _extract_image(self, content, url):
        """Extract a relevant image URL from content."""
        # Default image if none found
        default_image = 'https://source.unsplash.com/random/800x500/?brain,medical'
        
        # Check if content has images
        if 'image' in content and content['image']:
            return content['image']
        
        try:
            # Try to extract image from page
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for og:image meta tag
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    return og_image.get('content')
                
                # Look for main image
                main_image = soup.find('img', class_='main') or soup.find('img', class_='featured') or soup.find('img', class_='hero') or soup.find('img', class_='banner')
                if main_image and main_image.get('src'):
                    img_src = main_image.get('src')
                    # Convert relative URL to absolute
                    if img_src and not str(img_src).startswith('http'):
                        img_src = urljoin(url, str(img_src))
                    return img_src
                
                # Look for first large image
                images = soup.find_all('img')
                for img in images:
                    if img.get('width') and int(img['width']) > 300:
                        img_src = img['src']
                        # Convert relative URL to absolute
                        if not img_src.startswith('http'):
                            img_src = urljoin(url, img_src)
                        return img_src
        
        except Exception as e:
            self.logger.error(f"Error extracting image from {url}: {str(e)}")
        
        return default_image
    
    def _categorize_tip(self, title, content):
        """Categorize tip based on content."""
        categories = {
            'Communication': ['speak', 'talk', 'communication', 'language', 'verbal'],
            'Daily Care': ['routine', 'daily', 'hygiene', 'bathing', 'dressing'],
            'Activities': ['activity', 'exercise', 'engage', 'stimulation', 'game'],
            'Environment': ['home', 'environment', 'safety', 'lighting', 'noise'],
            'Nutrition': ['food', 'eat', 'nutrition', 'diet', 'meal'],
            'Behavioral Challenges': ['behavior', 'agitation', 'wandering', 'aggression', 'mood'],
            'Caregiver Self-Care': ['caregiver', 'self-care', 'stress', 'burnout', 'support']
        }
        
        text = title.lower() + ' ' + content.lower()
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return 'General Tips'
    
    def _save_articles(self, articles):
        """Save articles to JSON file."""
        try:
            # Check if file exists and read existing articles
            existing_articles = []
            if os.path.exists(self.articles_file):
                with open(self.articles_file, 'r') as f:
                    existing_articles = json.load(f)
            
            # Combine with new articles and save
            all_articles = existing_articles + articles
            
            # Ensure unique IDs
            for i, article in enumerate(all_articles):
                article['id'] = i + 1
            
            with open(self.articles_file, 'w') as f:
                json.dump(all_articles, f, indent=2)
            
            self.logger.info(f"Saved {len(articles)} new articles, total: {len(all_articles)}")
        
        except Exception as e:
            self.logger.error(f"Error saving articles: {str(e)}")
    
    def _save_tips(self, tips):
        """Save tips to JSON file."""
        try:
            # Check if file exists and read existing tips
            existing_tips = []
            if os.path.exists(self.tips_file):
                with open(self.tips_file, 'r') as f:
                    existing_tips = json.load(f)
            
            # Combine with new tips and save
            all_tips = existing_tips + tips
            
            # Ensure unique IDs
            for i, tip in enumerate(all_tips):
                tip['id'] = i + 1
            
            with open(self.tips_file, 'w') as f:
                json.dump(all_tips, f, indent=2)
            
            self.logger.info(f"Saved {len(tips)} new tips, total: {len(all_tips)}")
        
        except Exception as e:
            self.logger.error(f"Error saving tips: {str(e)}")
    
    def run_scheduled_crawl(self):
        """Run a scheduled crawl job."""
        self.logger.info("Starting scheduled crawl job")
        results = self.crawl_sources()
        self.logger.info(f"Scheduled crawl complete. Fetched {results['articles_count']} articles and {results['tips_count']} tips")
        return results