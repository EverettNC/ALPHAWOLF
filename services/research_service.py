import json
import os
import logging
from datetime import datetime, timedelta
import openai
from openai import OpenAI
import trafilatura

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class ResearchService:
    """
    Service for gathering and managing research information about dementia and Alzheimer's
    using OpenAI's language models and web scraping.
    """
    
    def __init__(self):
        self.research_data_path = "data/research_data.json"
        self.research_data = self._load_research_data()
        self.daily_tips_path = "data/daily_tips.json"
        self.daily_tips = self._load_daily_tips()
        self.expert_insights_path = "data/expert_insights.json"
        self.expert_insights = self._load_expert_insights()
        self.resources_path = "data/resources.json"
        self.resources = self._load_resources()
        
        # Ensure the data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Check if the research data is stale (last updated > 7 days ago)
        self._check_and_update_research_data()
        
        logger.info("Research service initialized")
    
    def _load_json_data(self, path, default=None):
        """Helper to load JSON files with default fallback."""
        if default is None:
            default = {
                "last_updated": (datetime.now() - timedelta(days=30)).isoformat(),
                "items": []
            }
            
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
            return default
        except Exception as e:
            logger.error(f"Error loading JSON from {path}: {e}")
            return default
    
    def _save_json_data(self, data, path):
        """Helper to save data to JSON file."""
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON to {path}: {e}")
            return False
    
    def _load_research_data(self):
        """Load research article data from JSON file."""
        return self._load_json_data(self.research_data_path)
    
    def _load_daily_tips(self):
        """Load daily tips data from JSON file."""
        return self._load_json_data(self.daily_tips_path)
    
    def _load_expert_insights(self):
        """Load expert insights data from JSON file."""
        return self._load_json_data(self.expert_insights_path)
    
    def _load_resources(self):
        """Load resources data from JSON file."""
        return self._load_json_data(self.resources_path)
    
    def _check_and_update_research_data(self):
        """Check if research data is stale and update if needed."""
        try:
            last_updated = datetime.fromisoformat(self.research_data.get("last_updated", "2000-01-01"))
            now = datetime.now()
            
            # Update if older than 7 days
            if (now - last_updated).days > 7:
                logger.info("Research data is stale. Updating...")
                self.update_research_data()
        except Exception as e:
            logger.error(f"Error checking research data: {e}")
    
    def update_research_data(self):
        """Gather new research information using OpenAI."""
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a neuroscience and dementia research specialist. "
                                                "Your task is to provide the latest research findings and breakthroughs "
                                                "in Alzheimer's and dementia research. Format your response as JSON."},
                    {"role": "user", "content": "Generate 6 recent research articles or findings about Alzheimer's disease "
                                              "and dementia from the past year. Include title, publication date (use recent dates from "
                                              "the last few months in 2025), brief summary, and key findings for each. "
                                              "Format as JSON with this structure: {\"articles\": [{\"title\": \"...\", "
                                              "\"date\": \"YYYY-MM-DD\", \"summary\": \"...\", \"key_findings\": \"...\"}]}"}
                ],
                response_format={"type": "json_object"}
            )
            
            articles_data = json.loads(response.choices[0].message.content)
            
            # Update the research data
            self.research_data = {
                "last_updated": datetime.now().isoformat(),
                "items": articles_data.get("articles", [])
            }
            
            # Save the updated data
            self._save_json_data(self.research_data, self.research_data_path)
            logger.info(f"Updated research data with {len(self.research_data['items'])} articles")
            return True
        except Exception as e:
            logger.error(f"Error updating research data: {e}")
            return False
    
    def update_daily_tips(self):
        """Generate new daily tips using OpenAI."""
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert in dementia care and daily management. "
                                                "Your task is to provide practical, helpful tips for people living with "
                                                "dementia and their caregivers. Format your response as JSON."},
                    {"role": "user", "content": "Generate 20 practical daily tips for dementia care, covering areas like "
                                              "communication, environment, activities, nutrition, safety, and caregiving self-care. "
                                              "Format as JSON with this structure: {\"tips\": [{\"category\": \"...\", "
                                              "\"title\": \"...\", \"content\": \"...\"}]}"}
                ],
                response_format={"type": "json_object"}
            )
            
            tips_data = json.loads(response.choices[0].message.content)
            
            # Update the daily tips data
            self.daily_tips = {
                "last_updated": datetime.now().isoformat(),
                "items": tips_data.get("tips", [])
            }
            
            # Save the updated data
            self._save_json_data(self.daily_tips, self.daily_tips_path)
            logger.info(f"Updated daily tips with {len(self.daily_tips['items'])} tips")
            return True
        except Exception as e:
            logger.error(f"Error updating daily tips: {e}")
            return False
    
    def update_expert_insights(self):
        """Generate new expert insights using OpenAI."""
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a panel of diverse dementia experts including neurologists, "
                                                "geriatricians, caregiving specialists, and researchers. "
                                                "Your task is to provide insightful expert commentary on various aspects "
                                                "of dementia care and management. Format your response as JSON."},
                    {"role": "user", "content": "Generate 10 expert insights about dementia care and management. For each insight, "
                                              "include the expert's name, their specialty/title, a quote, and 2-3 related topics. "
                                              "Make the experts diverse in background, specialization, and perspective. "
                                              "Format as JSON with this structure: {\"insights\": [{\"expert_name\": \"...\", "
                                              "\"title\": \"...\", \"quote\": \"...\", \"topics\": [\"...\", \"...\"]"}
                ],
                response_format={"type": "json_object"}
            )
            
            insights_data = json.loads(response.choices[0].message.content)
            
            # Update the expert insights data
            self.expert_insights = {
                "last_updated": datetime.now().isoformat(),
                "items": insights_data.get("insights", [])
            }
            
            # Save the updated data
            self._save_json_data(self.expert_insights, self.expert_insights_path)
            logger.info(f"Updated expert insights with {len(self.expert_insights['items'])} insights")
            return True
        except Exception as e:
            logger.error(f"Error updating expert insights: {e}")
            return False
    
    def update_resources(self):
        """Generate dementia resources using OpenAI."""
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a dementia resources specialist who catalogs the most helpful "
                                                "books, websites, guides, and support systems for people affected by dementia. "
                                                "Your task is to compile comprehensive resource lists for various needs. "
                                                "Format your response as JSON."},
                    {"role": "user", "content": "Create a comprehensive resource list for dementia care, including: "
                                              "1. Books (title, author, brief description) "
                                              "2. Websites (name, URL, description) "
                                              "3. Downloadable guides (title, focus area) "
                                              "4. Support groups (name, type, purpose) "
                                              "Format as JSON with this structure: {\"resources\": {\"books\": [{...}], "
                                              "\"websites\": [{...}], \"guides\": [{...}], \"support_groups\": [{...}]}}"}
                ],
                response_format={"type": "json_object"}
            )
            
            resources_data = json.loads(response.choices[0].message.content)
            
            # Update the resources data
            self.resources = {
                "last_updated": datetime.now().isoformat(),
                "items": resources_data.get("resources", {})
            }
            
            # Save the updated data
            self._save_json_data(self.resources, self.resources_path)
            logger.info("Updated resources data")
            return True
        except Exception as e:
            logger.error(f"Error updating resources: {e}")
            return False
    
    def get_research_articles(self, limit=10):
        """Get the most recent research articles."""
        return self.research_data.get("items", [])[:limit]
    
    def get_daily_tip(self):
        """Get a random daily tip."""
        import random
        items = self.daily_tips.get("items", [])
        return random.choice(items) if items else None
    
    def get_expert_insights(self, limit=10):
        """Get expert insights."""
        return self.expert_insights.get("items", [])[:limit]
    
    def get_resources(self, resource_type=None):
        """Get resources, optionally filtered by type."""
        resources = self.resources.get("items", {})
        if resource_type and resource_type in resources:
            return resources.get(resource_type, [])
        return resources
    
    def search_research(self, query, limit=5):
        """
        Search for research articles matching the query.
        
        This is a simplified search that checks if query terms appear in the title or summary.
        In a production environment, this would use more sophisticated search techniques.
        """
        query = query.lower()
        query_terms = query.split()
        results = []
        
        for article in self.research_data.get("items", []):
            title = article.get("title", "").lower()
            summary = article.get("summary", "").lower()
            content = title + " " + summary
            
            # Simple matching algorithm - count how many query terms appear in the content
            match_count = sum(1 for term in query_terms if term in content)
            
            if match_count > 0:
                article["relevance"] = match_count / len(query_terms)
                results.append(article)
        
        # Sort by relevance score
        results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        return results[:limit]
    
    def fetch_article_from_url(self, url):
        """
        Fetch and extract content from a URL using trafilatura.
        Then summarize it using OpenAI.
        """
        try:
            # Download and extract main content
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded)
            
            if not text:
                return {"success": False, "error": "Could not extract content from URL"}
            
            # Summarize the content using OpenAI
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a dementia research specialist. "
                                                "Your task is to summarize articles about dementia and Alzheimer's research "
                                                "in a way that is informative, accurate, and accessible to caregivers and patients."},
                    {"role": "user", "content": f"Summarize the following article about dementia/Alzheimer's research. "
                                              f"Include the main findings, implications for patients or caregivers, and any "
                                              f"limitations mentioned. Keep the summary concise but comprehensive:\n\n{text[:8000]}"}
                ]
            )
            
            summary = response.choices[0].message.content
            
            return {
                "success": True,
                "original_content": text[:10000],  # Limit to first 10000 chars
                "summary": summary,
                "url": url
            }
            
        except Exception as e:
            logger.error(f"Error fetching article: {e}")
            return {"success": False, "error": str(e)}