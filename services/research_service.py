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
import json
import logging
import os
import random
from datetime import datetime

class ResearchService:
    """Service for providing research articles, daily tips, and other learning resources."""
    
    def __init__(self):
        """Initialize the research service by loading data from JSON files."""
        self.logger = logging.getLogger(__name__)
        self.articles = []
        self.tips = []
        self.resources = {}
        self.expert_insights = []
        
        # Load data
        self._load_articles()
        self._load_tips()
        self._load_resources()
        self._load_expert_insights()
        
        self.logger.info("Research service initialized")
    
    def _load_articles(self):
        """Load research articles from JSON file."""
        try:
            articles_path = os.path.join('data', 'research_articles.json')
            if os.path.exists(articles_path):
                with open(articles_path, 'r') as f:
                    self.articles = json.load(f)
                self.logger.info(f"Loaded {len(self.articles)} articles")
            else:
                # Create sample articles if file doesn't exist
                self.articles = self._generate_sample_articles()
                self.logger.warning("Articles file not found. Using sample data.")
        except Exception as e:
            self.logger.error(f"Error loading articles: {str(e)}")
            self.articles = self._generate_sample_articles()
    
    def _load_tips(self):
        """Load daily tips from JSON file."""
        try:
            tips_path = os.path.join('data', 'daily_tips.json')
            if os.path.exists(tips_path):
                with open(tips_path, 'r') as f:
                    self.tips = json.load(f)
                self.logger.info(f"Loaded {len(self.tips)} tips")
            else:
                # Create sample tips if file doesn't exist
                self.tips = self._generate_sample_tips()
                self.logger.warning("Tips file not found. Using sample data.")
        except Exception as e:
            self.logger.error(f"Error loading tips: {str(e)}")
            self.tips = self._generate_sample_tips()
    
    def _load_resources(self):
        """Load resources from JSON file."""
        try:
            resources_path = os.path.join('data', 'resources.json')
            if os.path.exists(resources_path):
                with open(resources_path, 'r') as f:
                    self.resources = json.load(f)
                self.logger.info(f"Loaded resources with {len(self.resources.keys())} categories")
            else:
                # Create sample resources if file doesn't exist
                self.resources = self._generate_sample_resources()
                self.logger.warning("Resources file not found. Using sample data.")
        except Exception as e:
            self.logger.error(f"Error loading resources: {str(e)}")
            self.resources = self._generate_sample_resources()
    
    def _load_expert_insights(self):
        """Load expert insights from JSON file."""
        try:
            insights_path = os.path.join('data', 'expert_insights.json')
            if os.path.exists(insights_path):
                with open(insights_path, 'r') as f:
                    self.expert_insights = json.load(f)
                self.logger.info(f"Loaded {len(self.expert_insights)} expert insights")
            else:
                # Create sample insights if file doesn't exist
                self.expert_insights = self._generate_sample_expert_insights()
                self.logger.warning("Expert insights file not found. Using sample data.")
        except Exception as e:
            self.logger.error(f"Error loading expert insights: {str(e)}")
            self.expert_insights = self._generate_sample_expert_insights()
    
    def get_research_articles(self, limit=None, topic=None):
        """Get research articles, optionally filtered by topic and limited to a specific number."""
        filtered_articles = self.articles
        
        if topic:
            filtered_articles = [a for a in filtered_articles if topic.lower() in [t.lower() for t in a.get('topics', [])]]
        
        if limit and limit > 0:
            return filtered_articles[:limit]
        
        return filtered_articles
    
    def get_article_by_id(self, article_id):
        """Get a specific article by its ID."""
        for article in self.articles:
            if article.get('id') == article_id:
                return article
        return None
    
    def get_related_articles(self, article_id, limit=3):
        """Get articles related to the given article."""
        article = self.get_article_by_id(article_id)
        if not article:
            return []
        
        # Find articles with similar topics
        article_topics = set(article.get('topics', []))
        if not article_topics:
            # If no topics, just return random articles excluding the current one
            other_articles = [a for a in self.articles if a.get('id') != article_id]
            return random.sample(other_articles, min(limit, len(other_articles)))
        
        # Calculate relevance score for each article based on topic overlap
        scored_articles = []
        for a in self.articles:
            if a.get('id') == article_id:
                continue
            
            a_topics = set(a.get('topics', []))
            if not a_topics:
                continue
            
            # Score based on topic overlap
            overlap = len(article_topics.intersection(a_topics))
            scored_articles.append((a, overlap))
        
        # Sort by relevance score (descending)
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N articles
        return [a[0] for a in scored_articles[:limit]]
    
    def get_daily_tip(self):
        """Get a daily tip. Changes each day."""
        if not self.tips:
            return None
        
        # Use the day of year to select a consistent tip for each day
        day_of_year = datetime.now().timetuple().tm_yday
        return self.tips[day_of_year % len(self.tips)]
    
    def get_all_tips(self):
        """Get all tips."""
        return self.tips
    
    def get_expert_insights(self, limit=None):
        """Get expert insights, optionally limited to a specific number."""
        if limit and limit > 0:
            return self.expert_insights[:limit]
        return self.expert_insights
    
    def get_resources(self):
        """Get all resources."""
        return self.resources
    
    def _generate_sample_articles(self):
        """Generate sample articles for testing."""
        return [
            {
                'id': 1,
                'title': 'Advances in Early Detection of Alzheimer\'s Disease',
                'summary': 'New research shows promising results in early detection of Alzheimer\'s biomarkers, potentially allowing for earlier intervention.',
                'content': '<p>Recent advances in neuroimaging and blood-based biomarkers have shown significant promise in detecting Alzheimer\'s disease years before cognitive symptoms appear. This study explores the latest techniques and their potential impact on treatment outcomes.</p><p>Researchers at the National Institute on Aging have developed a new blood test that can detect specific protein changes associated with Alzheimer\'s with 94% accuracy, compared to more invasive and expensive methods like spinal fluid analysis.</p><p>Early detection could allow for interventions when they might be most effective - before significant brain damage has occurred. This could potentially change the trajectory of the disease for millions of people worldwide.</p>',
                'date': 'May 5, 2025',
                'authors': 'Dr. Elena Rodriguez, Dr. James Chen',
                'institution': 'National Institute on Aging',
                'topics': ['Prevention', 'Diagnosis', 'Research'],
                'image_url': 'https://source.unsplash.com/random/800x500/?brain,medical',
                'abstract': 'Early detection of Alzheimer\'s disease biomarkers may allow for intervention before significant cognitive decline occurs. This study reviews recent advances in neuroimaging and blood-based biomarkers that show promise for clinical application.',
                'key_findings': [
                    'Blood tests can now detect Alzheimer\'s biomarkers with 94% accuracy',
                    'Changes can be detected up to 15 years before cognitive symptoms appear',
                    'Early intervention may significantly slow disease progression',
                    'Combined biomarker approach increases diagnostic certainty'
                ],
                'practical_applications': [
                    'Annual cognitive screening for high-risk individuals over 50',
                    'Combination of blood tests with cognitive assessments',
                    'Lifestyle interventions at the first sign of biomarker changes',
                    'Targeted therapies based on specific biomarker profiles'
                ],
                'references': [
                    'Smith J, et al. (2024). "Blood-based biomarkers for early Alzheimer\'s detection." Journal of Neurology, 45(3), 234-246.',
                    'Chen T, et al. (2024). "Longitudinal changes in plasma phosphorylated tau181 and related biomarkers." Alzheimer\'s & Dementia, 20(1), 22-35.',
                    'Williams C, et al. (2023). "Meta-analysis of blood-based biomarkers for Alzheimer\'s disease." Nature Reviews Neurology, 19(8), 456-470.'
                ],
                'glossary': [
                    {'term': 'Biomarker', 'definition': 'A measurable substance in an organism whose presence is indicative of some disease or infection'},
                    {'term': 'Tau protein', 'definition': 'A protein that stabilizes microtubules in neurons, which can become abnormally phosphorylated in Alzheimer\'s disease'},
                    {'term': 'Amyloid beta', 'definition': 'A peptide that is the main component of amyloid plaques found in the brains of people with Alzheimer\'s disease'}
                ]
            },
            {
                'id': 2,
                'title': 'Mediterranean Diet and Cognitive Health',
                'summary': 'Recent studies link Mediterranean diet adherence with slower cognitive decline in adults with early-stage dementia.',
                'content': '<p>The Mediterranean diet, rich in olive oil, nuts, fish, whole grains, and fresh produce, has long been associated with cardiovascular benefits. New research now suggests it may also provide significant protection against cognitive decline.</p><p>In a five-year study of 1,200 participants aged 65-80 with mild cognitive impairment, those who adhered closely to a Mediterranean diet showed 32% less cognitive decline compared to those following a typical Western diet.</p><p>The study also identified specific components of the diet that appear to be most beneficial, including omega-3 fatty acids from fish, polyphenols from olive oil and berries, and various antioxidants from colorful vegetables.</p>',
                'date': 'April 28, 2025',
                'authors': 'Dr. Sofia Papadopoulos, Dr. Michael Hernandez',
                'institution': 'Mediterranean Nutrition Research Institute',
                'topics': ['Nutrition', 'Prevention', 'Lifestyle'],
                'image_url': 'https://source.unsplash.com/random/800x500/?mediterranean,food',
                'abstract': 'This longitudinal study examined the relationship between adherence to a Mediterranean dietary pattern and cognitive decline in older adults with mild cognitive impairment. Results indicate significant protective effects of this dietary pattern on cognitive function.',
                'key_findings': [
                    '32% reduction in cognitive decline with high Mediterranean diet adherence',
                    'Omega-3 rich fish consumption (2+ servings/week) provided strongest benefits',
                    'Olive oil consumption showed dose-dependent relationship with cognitive protection',
                    'Benefits were observed even when diet changes began after age 65'
                ],
                'practical_applications': [
                    'Gradually transition to Mediterranean eating patterns',
                    'Prioritize olive oil as primary fat source',
                    'Include fatty fish at least twice weekly',
                    'Minimize processed foods and added sugars'
                ],
                'references': [
                    'Papadopoulos S, et al. (2025). "Mediterranean diet and rate of cognitive decline in early dementia: The MEDAS Cohort." Journal of Nutrition, Health & Aging, 29(2), 122-134.',
                    'Hernandez M, et al. (2024). "Components of Mediterranean diet associated with preserved cognitive function." Alzheimer\'s & Dementia, 20(3), 245-258.',
                    'Garcia T, et al. (2023). "Systematic review of dietary patterns and cognitive outcomes." Clinical Nutrition, 42(1), 67-82.'
                ],
                'glossary': [
                    {'term': 'Polyphenols', 'definition': 'Micronutrients with antioxidant properties found in plant-based foods'},
                    {'term': 'Omega-3 fatty acids', 'definition': 'Essential fatty acids found in fish, flaxseeds, and some nuts that have anti-inflammatory properties'},
                    {'term': 'Mild Cognitive Impairment', 'definition': 'A condition characterized by a slight but noticeable decline in cognitive abilities, including memory and thinking skills'}
                ]
            },
            {
                'id': 3,
                'title': 'Sleep Quality and Memory Preservation',
                'summary': 'New findings suggest that improving sleep quality may help preserve memory function in people with mild cognitive impairment.',
                'content': '<p>Sleep disturbances are common in dementia and Alzheimer\'s disease, but mounting evidence suggests they may also contribute to cognitive decline rather than just being a symptom. A groundbreaking study has now demonstrated that targeted sleep interventions can slow memory loss in at-risk populations.</p><p>The two-year clinical trial involved 300 participants with mild cognitive impairment who received either standard care or a comprehensive sleep improvement program. The intervention group showed significant improvements in sleep quality and, more importantly, 28% better memory retention over the study period.</p><p>The sleep program included cognitive behavioral therapy for insomnia, light therapy, and sleep hygiene education. Researchers monitored sleep patterns using both sleep studies and wearable technology.</p>',
                'date': 'April 15, 2025',
                'authors': 'Dr. Robert Chen, Dr. Aisha Johnson',
                'institution': 'Sleep and Cognition Research Center',
                'topics': ['Sleep', 'Memory', 'Intervention'],
                'image_url': 'https://source.unsplash.com/random/800x500/?sleep,bedroom',
                'abstract': 'This study investigated whether improving sleep quality through behavioral and environmental interventions could affect memory outcomes in individuals with mild cognitive impairment. Results indicate that targeted sleep interventions may be an effective non-pharmacological approach to slowing cognitive decline.',
                'key_findings': [
                    '28% better memory retention in intervention group over two years',
                    'Improvements in deep sleep correlated most strongly with cognitive benefits',
                    'Sleep continuity more important than total sleep duration',
                    'Benefits persisted at 6-month follow-up after intervention ended'
                ],
                'practical_applications': [
                    'Maintain consistent sleep and wake times',
                    'Create a dark, cool, and quiet sleep environment',
                    'Avoid screens for 1-2 hours before bedtime',
                    'Consider CBT-I (Cognitive Behavioral Therapy for Insomnia) for persistent sleep problems'
                ],
                'references': [
                    'Chen R, et al. (2025). "Sleep intervention and memory outcomes in mild cognitive impairment." Sleep Medicine, 76, 45-58.',
                    'Johnson A, et al. (2024). "Slow-wave sleep and cognitive function in older adults." Journal of Sleep Research, 33(2), 112-125.',
                    'Wilson B, et al. (2023). "Meta-analysis of sleep interventions in dementia care." Neurology, 100(5), 432-445.'
                ],
                'glossary': [
                    {'term': 'Sleep architecture', 'definition': 'The structure of sleep, including different stages like REM and non-REM sleep'},
                    {'term': 'Circadian rhythm', 'definition': 'The natural, internal process that regulates the sleep-wake cycle, repeating roughly every 24 hours'},
                    {'term': 'Sleep hygiene', 'definition': 'Practices and habits necessary to have good nighttime sleep quality and full daytime alertness'}
                ]
            }
        ]
    
    def _generate_sample_tips(self):
        """Generate sample tips for testing."""
        return [
            {
                'id': 1,
                'title': 'Morning Routines',
                'content': 'Establishing a consistent morning routine can help reduce anxiety and confusion. Consider creating a visual checklist of morning activities such as brushing teeth, getting dressed, and having breakfast.',
                'category': 'Daily Care',
                'date': 'May 10, 2025',
                'source': 'Alzheimer\'s Association'
            },
            {
                'id': 2,
                'title': 'Communication Strategies',
                'content': 'Speak clearly and in simple sentences. Allow extra time for the person to process information and respond. Avoid asking multiple questions at once, which can cause confusion.',
                'category': 'Communication',
                'date': 'May 9, 2025',
                'source': 'Dementia Care Center'
            },
            {
                'id': 3,
                'title': 'Meal Simplification',
                'content': 'Simplify mealtime decisions by offering limited choices. Use contrasting colors for plates and food to make meals more visually accessible. Serve one food at a time if multiple items on a plate seem overwhelming.',
                'category': 'Nutrition',
                'date': 'May 8, 2025',
                'source': 'National Institute on Aging'
            },
            {
                'id': 4,
                'title': 'Music Therapy Benefits',
                'content': 'Playing familiar songs from a person\'s young adult years can evoke positive emotions and memories. Music therapy has been shown to reduce agitation and improve mood even in advanced dementia.',
                'category': 'Activities',
                'date': 'May 7, 2025',
                'source': 'Journal of Music Therapy'
            },
            {
                'id': 5,
                'title': 'Home Safety Adaptations',
                'content': 'Remove tripping hazards like loose rugs, reduce clutter, and ensure good lighting throughout the home. Install grab bars in bathrooms and use contrasting colors to highlight steps and transitions between rooms.',
                'category': 'Environment',
                'date': 'May 6, 2025',
                'source': 'Home Safety Council'
            },
            {
                'id': 6,
                'title': 'Managing Sundowning',
                'content': 'Sundowning—increased confusion and agitation in the late afternoon or evening—can be reduced by maintaining a predictable routine, ensuring adequate lighting, and limiting caffeine and naps during the day.',
                'category': 'Behavioral Challenges',
                'date': 'May 5, 2025',
                'source': 'Sleep Research Institute'
            },
            {
                'id': 7,
                'title': 'Caregiver Self-Care',
                'content': 'Schedule short breaks throughout the day, even if just for 10 minutes. Use relaxation techniques like deep breathing or progressive muscle relaxation. Remember that taking care of yourself is essential for providing good care to others.',
                'category': 'Caregiver Self-Care',
                'date': 'May 4, 2025',
                'source': 'Caregiver Support Network'
            }
        ]
    
    def _generate_sample_resources(self):
        """Generate sample resources for testing."""
        return {
            'books': [
                {
                    'title': 'The 36-Hour Day: A Family Guide to Caring for People Who Have Alzheimer\'s Disease',
                    'author': 'Nancy L. Mace and Peter V. Rabins',
                    'year': '2021',
                    'description': 'Practical advice for families and caregivers of those with Alzheimer\'s disease and other dementias.'
                },
                {
                    'title': 'Creating Moments of Joy Along the Alzheimer\'s Journey',
                    'author': 'Jolene Brackey',
                    'year': '2016',
                    'description': 'A guide to making the most of life at each stage of Alzheimer\'s disease.'
                },
                {
                    'title': 'Dementia Reimagined: Building a Life of Joy and Dignity from Beginning to End',
                    'author': 'Tia Powell',
                    'year': '2019',
                    'description': 'A groundbreaking approach to dementia care that focuses on dignity and quality of life.'
                },
                {
                    'title': 'The Alzheimer\'s Solution: A Revolutionary Guide to How You Can Prevent and Reverse Memory Loss',
                    'author': 'Dean Sherzai and Ayesha Sherzai',
                    'year': '2017',
                    'description': 'A neurologists\' guide to lifestyle interventions that may help prevent cognitive decline.'
                }
            ],
            'organizations': [
                {
                    'name': 'Alzheimer\'s Association',
                    'website': 'https://www.alz.org',
                    'description': 'Provides education, support groups, and resources for people with Alzheimer\'s and their caregivers.'
                },
                {
                    'name': 'National Institute on Aging',
                    'website': 'https://www.nia.nih.gov',
                    'description': 'Government resource for information on aging and age-related diseases including Alzheimer\'s.'
                },
                {
                    'name': 'Family Caregiver Alliance',
                    'website': 'https://www.caregiver.org',
                    'description': 'Support and resources specifically for family caregivers of adults with chronic conditions.'
                },
                {
                    'name': 'Dementia Society of America',
                    'website': 'https://www.dementiasociety.org',
                    'description': 'Advocacy and education focused on all forms of dementia, not just Alzheimer\'s.'
                }
            ],
            'apps': [
                {
                    'name': 'Dementia Talk',
                    'platform': 'iOS, Android',
                    'description': 'App to track behavior patterns, manage medications, and coordinate care.'
                },
                {
                    'name': 'Lumosity',
                    'platform': 'iOS, Android, Web',
                    'description': 'Brain training games designed to exercise memory, attention, and cognitive skills.'
                },
                {
                    'name': 'MindMate',
                    'platform': 'iOS, Android',
                    'description': 'Comprehensive app for brain health including games, exercise videos, nutrition guidance, and more.'
                },
                {
                    'name': 'Timeless',
                    'platform': 'iOS',
                    'description': 'Photo-based reminder app with facial recognition designed specifically for people with dementia.'
                }
            ],
            'videos': [
                {
                    'title': 'Understanding Alzheimer\'s and Dementia',
                    'source': 'Alzheimer\'s Association',
                    'url': 'https://example.com/video1',
                    'duration': '12:34',
                    'description': 'Overview of how Alzheimer\'s affects the brain and the difference between Alzheimer\'s and dementia.'
                },
                {
                    'title': 'Caregiver Training: Agitation and Anxiety',
                    'source': 'UCLA Alzheimer\'s and Dementia Care Program',
                    'url': 'https://example.com/video2',
                    'duration': '18:42',
                    'description': 'Strategies for managing agitation and anxiety in people with dementia.'
                },
                {
                    'title': 'Communication Techniques for Dementia',
                    'source': 'National Institute on Aging',
                    'url': 'https://example.com/video3',
                    'duration': '15:10',
                    'description': 'Effective communication methods when interacting with someone with dementia.'
                },
                {
                    'title': 'Creating a Dementia-Friendly Home',
                    'source': 'Dementia Society',
                    'url': 'https://example.com/video4',
                    'duration': '22:15',
                    'description': 'Room-by-room guide to making a home safer and more navigable for someone with dementia.'
                }
            ]
        }
    
    def _generate_sample_expert_insights(self):
        """Generate sample expert insights for testing."""
        return [
            {
                'id': 1,
                'expert_name': 'Dr. Maria Johnson',
                'title': 'Director of Cognitive Neuroscience, Memory Institute',
                'topic': 'The Role of Social Connection in Brain Health',
                'content': 'Recent research highlights the profound impact that social connections have on brain health. Studies show that individuals with strong social networks experience slower cognitive decline compared to those who are socially isolated. This appears to be mediated through multiple pathways, including reduced stress, increased cognitive stimulation through conversation, and improved health behaviors. I recommend that families of those with dementia focus on maintaining meaningful social interactions, even as communication abilities change.',
                'date': 'May 8, 2025',
                'image_url': 'https://source.unsplash.com/random/150x150/?professor,woman'
            },
            {
                'id': 2,
                'expert_name': 'Dr. David Park',
                'title': 'Clinical Director, Dementia Care Center',
                'topic': 'Rethinking Behavioral Symptoms',
                'content': 'When we see "challenging behaviors" in dementia, we should view these as communications of unmet needs rather than problems to be managed. For example, wandering may indicate boredom or a need for exercise, while agitation might signal pain, hunger, or overstimulation. By addressing the underlying need rather than just the behavior, we can improve quality of life and reduce caregiver stress. This approach requires careful observation and detective work but leads to more humane and effective care.',
                'date': 'May 1, 2025',
                'image_url': 'https://source.unsplash.com/random/150x150/?doctor,asian'
            },
            {
                'id': 3,
                'expert_name': 'Sarah Williams, MSW',
                'title': 'Gerontological Social Worker',
                'topic': 'Supporting the Caregiver Journey',
                'content': 'Caregiving for someone with dementia is a marathon, not a sprint. The most successful caregivers I\'ve worked with prioritize their own well-being alongside the person they care for. This means setting boundaries, accepting help, connecting with support groups, and finding moments of joy in each day. Remember that the airline safety instruction to "put on your own oxygen mask first" applies to caregiving too. Taking care of yourself isn\'t selfish—it\'s necessary for sustainable caregiving.',
                'date': 'April 22, 2025',
                'image_url': 'https://source.unsplash.com/random/150x150/?social,worker'
            }
        ]