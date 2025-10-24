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
AlphaVox - Knowledge Integration Module
---------------------------------------
This module provides integration between AlphaVox and knowledge sources,
including both internal knowledge bases and external APIs.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Singleton instance
_knowledge_integration = None


class KnowledgeIntegration:
    """Handles integration between AlphaVox and knowledge sources.

    This class provides:
    - Access to the knowledge engine
    - Query processing for knowledge retrieval
    - Integration with external knowledge APIs
    """

    def __init__(self):
        """Initialize knowledge integration."""
        # Knowledge sources
        self.knowledge_engine = None
        self.external_apis = {}

        # Knowledge base paths
        self.knowledge_base_dir = os.path.join("attached_assets")
        self.facts_file = os.path.join(self.knowledge_base_dir, "facts.json")
        self.topics_file = os.path.join(self.knowledge_base_dir, "topics.json")
        self.knowledge_graph_file = os.path.join(
            self.knowledge_base_dir, "knowledge_graph.json"
        )

        # Initialize components
        self._initialize_components()

        # Load knowledge base
        self._load_knowledge_base()

        logger.info("Knowledge Integration initialized")

    def _initialize_components(self):
        """Initialize knowledge components."""
        # Try to load the knowledge engine
        try:
            from attached_assets.knowledge_engine import KnowledgeEngine

            self.knowledge_engine = KnowledgeEngine()
            logger.info("Knowledge engine loaded")
        except ImportError:
            logger.warning("Knowledge engine not available")

    def _load_knowledge_base(self):
        """Load knowledge base from files."""
        # Load facts
        self.facts = []
        if os.path.exists(self.facts_file):
            try:
                with open(self.facts_file, "r") as f:
                    self.facts = json.load(f)
                logger.info(f"Loaded {len(self.facts)} facts from knowledge base")
            except Exception as e:
                logger.error(f"Error loading facts: {e}")

        # Load topics
        self.topics = []
        if os.path.exists(self.topics_file):
            try:
                with open(self.topics_file, "r") as f:
                    self.topics = json.load(f)
                logger.info(f"Loaded {len(self.topics)} topics from knowledge base")
            except Exception as e:
                logger.error(f"Error loading topics: {e}")

        # Load knowledge graph
        self.knowledge_graph = {}
        if os.path.exists(self.knowledge_graph_file):
            try:
                with open(self.knowledge_graph_file, "r") as f:
                    self.knowledge_graph = json.load(f)
                logger.info(
                    f"Loaded knowledge graph with {len(self.knowledge_graph)} nodes"
                )
            except Exception as e:
                logger.error(f"Error loading knowledge graph: {e}")

    def query_knowledge_base(
        self, query: str, topic: Optional[str] = None, max_results: int = 5
    ) -> Dict[str, Any]:
        """Query the knowledge base for information.

        Args:
            query: Text query to search for
            topic: Optional topic to filter by
            max_results: Maximum number of results to return

        Returns:
            Dict with query results
        """
        # Try to use knowledge engine if available
        if self.knowledge_engine:
            try:
                result = self.knowledge_engine.query(query, topic, max_results)
                if result:
                    return result
            except Exception as e:
                logger.error(f"Error querying knowledge engine: {e}")

        # Fall back to basic search
        results = []

        # Filter by topic if provided
        filtered_facts = self.facts
        if topic:
            filtered_facts = [f for f in self.facts if f.get("topic") == topic]

        # Simple keyword matching (very basic)
        query_terms = query.lower().split()
        for fact in filtered_facts:
            text = fact.get("text", "").lower()
            score = sum(1 for term in query_terms if term in text)
            if score > 0:
                results.append(
                    {
                        "text": fact.get("text"),
                        "topic": fact.get("topic"),
                        "source": fact.get("source"),
                        "relevance": score / len(query_terms),
                    }
                )

        # Sort by relevance and limit results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        results = results[:max_results]

        return {
            "query": query,
            "topic": topic,
            "results": results,
            "count": len(results),
            "engine": "basic",
        }

    def get_topics(self) -> List[Dict[str, Any]]:
        """Get available topics in the knowledge base.

        Returns:
            List of topics with metadata
        """
        if self.knowledge_engine and hasattr(self.knowledge_engine, "get_topics"):
            try:
                return self.knowledge_engine.get_topics()
            except Exception as e:
                logger.error(f"Error getting topics from knowledge engine: {e}")

        return self.topics

    def get_related_topics(self, topic: str, limit: int = 5) -> List[str]:
        """Get topics related to the given topic.

        Args:
            topic: Topic to find related topics for
            limit: Maximum number of related topics to return

        Returns:
            List of related topic names
        """
        if self.knowledge_engine and hasattr(
            self.knowledge_engine, "get_related_topics"
        ):
            try:
                return self.knowledge_engine.get_related_topics(topic, limit)
            except Exception as e:
                logger.error(f"Error getting related topics from knowledge engine: {e}")

        # Basic fallback using knowledge graph
        if topic in self.knowledge_graph:
            related = self.knowledge_graph.get(topic, {}).get("related", [])
            return related[:limit]

        return []


def get_knowledge_integration():
    """Get or create the knowledge integration singleton."""
    global _knowledge_integration
    if _knowledge_integration is None:
        _knowledge_integration = KnowledgeIntegration()
    return _knowledge_integration
