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
AlphaVox Knowledge Engine
------------------------
This module enables AlphaVox to autonomously gather, process, and learn
from various information sources. It combines:

1. Web crawling for targeted information collection
2. Natural language processing for information extraction
3. Knowledge representation using graph-based structures
4. Active learning to expand knowledge in areas of uncertainty
5. Visible learning progress monitoring and reporting
"""

import datetime
import json
import logging
import os
import random
import threading
import time
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
KNOWLEDGE_DIR = "data/knowledge"
TOPICS_FILE = f"{KNOWLEDGE_DIR}/topics.json"
FACTS_FILE = f"{KNOWLEDGE_DIR}/facts.json"
LEARNING_LOG = f"{KNOWLEDGE_DIR}/learning_log.json"
CRAWLER_STATUS_FILE = f"{KNOWLEDGE_DIR}/crawler_status.json"

# Ensure knowledge directory exists
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

# Core topics for AlphaVox (extendable)
CORE_TOPICS = [
    "ai advancement",
    "react development",
    "speech recognition",
    "family and humanity",
]

# Source URLs for each topic
TOPIC_SOURCES = {
    "ai advancement": [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://www.technologyreview.com/topic/artificial-intelligence/",
    ],
    "react development": [
        "https://react.dev/",
        "https://blog.logrocket.com/tag/react/",
    ],
    "speech recognition": [
        "https://en.wikipedia.org/wiki/Speech_recognition",
        "https://deepgram.com/blog",
    ],
    "family and humanity": [
        "https://greatergood.berkeley.edu/",
        "https://www.psychologytoday.com/us/topics/family",
    ],
}


class KnowledgeGraph:
    """Represents knowledge as a graph of connected concepts."""

    def __init__(self, load_existing: bool = True):
        self.concepts = {}
        self.relationships = []
        self.topic_concepts = defaultdict(set)

        if load_existing:
            self._load()

    def add_concept(
        self, concept_id: str, name: str, data: Dict[str, Any], topics: List[str] = None
    ) -> str:
        if concept_id in self.concepts:
            self.concepts[concept_id].update(data)
        else:
            self.concepts[concept_id] = {
                "name": name,
                "last_updated": datetime.datetime.now().isoformat(),
                "confidence": 0.7,
                "data": data,
            }
        if topics:
            for topic in topics:
                self.topic_concepts[topic].add(concept_id)
        return concept_id

    def add_relationship(
        self,
        concept1_id: str,
        relationship: str,
        concept2_id: str,
        strength: float = 0.5,
    ) -> None:
        if concept1_id not in self.concepts or concept2_id not in self.concepts:
            return
        self.relationships.append(
            {
                "from": concept1_id,
                "relationship": relationship,
                "to": concept2_id,
                "strength": strength,
                "last_updated": datetime.datetime.now().isoformat(),
            }
        )

    def save(self) -> None:
        graph_file = f"{KNOWLEDGE_DIR}/knowledge_graph.json"
        topic_data = {topic: list(cids) for topic, cids in self.topic_concepts.items()}
        data = {
            "concepts": self.concepts,
            "relationships": self.relationships,
            "topic_concepts": topic_data,
            "last_updated": datetime.datetime.now().isoformat(),
        }
        with open(graph_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self) -> None:
        graph_file = f"{KNOWLEDGE_DIR}/knowledge_graph.json"
        if os.path.exists(graph_file):
            try:
                with open(graph_file, "r") as f:
                    data = json.load(f)
                    self.concepts = data.get("concepts", {})
                    self.relationships = data.get("relationships", [])
                    for topic, concept_ids in data.get("topic_concepts", {}).items():
                        self.topic_concepts[topic] = set(concept_ids)
            except Exception as e:
                logger.error(f"Error loading knowledge graph: {e}")


class FactManager:
    """Manages learned facts and their retrieval."""

    def __init__(self):
        self.facts = []
        self.by_topic = defaultdict(list)
        self.by_confidence = defaultdict(list)
        self._load_facts()

    def _load_facts(self):
        if os.path.exists(FACTS_FILE):
            try:
                with open(FACTS_FILE, "r") as f:
                    self.facts = json.load(f)
            except:
                self.facts = []

    def save_facts(self):
        with open(FACTS_FILE, "w") as f:
            json.dump(self.facts, f, indent=2)

    def add_fact(
        self,
        fact_text: str,
        source: str,
        topics: List[str],
        confidence: float = 0.7,
        metadata: Dict[str, Any] = None,
    ) -> int:
        fact = {
            "text": fact_text,
            "source": source,
            "topics": topics,
            "confidence": confidence,
            "metadata": metadata or {},
            "learned_at": datetime.datetime.now().isoformat(),
        }
        self.facts.append(fact)
        self.save_facts()
        return len(self.facts) - 1


class WebCrawler:
    """Live web crawler that gathers real knowledge on specified topics."""

    def __init__(self, topics: List[str] = None):
        self.running = False
        self.crawler_thread = None
        self.topics = topics or CORE_TOPICS
        self.status = {
            "running": False,
            "current_topic": None,
            "topics_processed": 0,
            "facts_discovered": 0,
            "last_update": None,
        }
        self._load_status()

    def _load_status(self):
        if os.path.exists(CRAWLER_STATUS_FILE):
            try:
                with open(CRAWLER_STATUS_FILE, "r") as f:
                    self.status = json.load(f)
            except:
                pass

    def _save_status(self):
        with open(CRAWLER_STATUS_FILE, "w") as f:
            json.dump(self.status, f, indent=2)

    def start(self):
        if self.running:
            return
        self.running = True
        self.status["running"] = True
        self._save_status()
        self.crawler_thread = threading.Thread(target=self._crawl_loop)
        self.crawler_thread.daemon = True
        self.crawler_thread.start()

    def stop(self):
        self.running = False
        self.status["running"] = False
        self._save_status()

    def get_status(self) -> Dict[str, Any]:
        return self.status

    def _crawl_loop(self):
        fact_manager = FactManager()
        knowledge_graph = KnowledgeGraph()
        while self.running:
            topic = random.choice(self.topics)
            self.status["current_topic"] = topic
            self._save_status()
            for url in TOPIC_SOURCES.get(topic, []):
                try:
                    r = requests.get(
                        url, headers={"User-Agent": "DerekBot/1.0"}, timeout=10
                    )
                    if r.status_code != 200:
                        continue
                    soup = BeautifulSoup(r.text, "html.parser")
                    for p in soup.find_all("p")[:5]:
                        text = p.get_text().strip()
                        if len(text.split()) < 6:
                            continue
                        fact_manager.add_fact(
                            text, source=url, topics=[topic], confidence=0.85
                        )
                        cid = f"{topic}_{int(time.time())}_{random.randint(1000, 9999)}"
                        knowledge_graph.add_concept(
                            cid, topic.title(), {"fact": text}, topics=[topic]
                        )
                        self.status["facts_discovered"] += 1
                        self._save_status()
                    knowledge_graph.save()
                except Exception as e:
                    logger.error(f"Error crawling {url}: {e}")
            self.status["topics_processed"] += 1
            self.status["last_update"] = datetime.datetime.now().isoformat()
            self._save_status()
            time.sleep(3)


class KnowledgeEngine:
    def __init__(self):
        self.graph = KnowledgeGraph()
        self.fact_manager = FactManager()
        self.crawler = WebCrawler()

    def start_learning(self):
        logger.info("Starting knowledge engine")
        self.crawler.start()

    def stop_learning(self):
        self.crawler.stop()

    def get_learning_metrics(self):
        return {
            "facts_learned": len(self.fact_manager.facts),
            "topics_explored": len(
                {t for f in self.fact_manager.facts for t in f.get("topics", [])}
            ),
            "last_updated": datetime.datetime.now().isoformat(),
            "crawler_status": self.crawler.get_status(),
        }


# Singleton
_knowledge_engine = None


def get_knowledge_engine():
    global _knowledge_engine
    if _knowledge_engine is None:
        _knowledge_engine = KnowledgeEngine()
    return _knowledge_engine


if __name__ == "__main__":
    engine = get_knowledge_engine()
    engine.start_learning()
    time.sleep(20)
    print(engine.get_learning_metrics())
    engine.stop_learning
