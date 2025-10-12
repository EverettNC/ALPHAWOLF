
"""
research_common.py
Shared utilities for research ingestion and curation.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict

@dataclass
class Paper:
    id: str
    title: str
    abstract: str
    url: str
    source: str
    published: datetime
    study_type: str
    peer_reviewed: bool
    sample_size: Optional[int] = None
    tags: Optional[List[str]] = None
    caution: Optional[str] = None
    quality_score: float = 0.0

    def to_item(self) -> Dict:
        d = asdict(self)
        d["published"] = self.published.isoformat()
        return d

def strength_label(score: float) -> str:
    if score >= 1.0: return "strong"
    if score >= 0.8: return "good"
    if score >= 0.6: return "moderate"
    return "preliminary"

def quality_score(study_type: str, peer_reviewed: bool, sample_size: Optional[int], published: datetime, caution: Optional[str]) -> float:
    type_weight = {
        'meta_analysis': 1.0,
        'systematic_review': 0.95,
        'rct': 0.9,
        'cohort': 0.7,
        'guideline': 0.6,
        'case_report': 0.3,
    }.get(study_type, 0.5)
    peer = 0.1 if peer_reviewed else -0.15
    size = 0.0 if not sample_size else min(0.2, sample_size / 5000.0 * 0.2)
    # recency light boost, max 0.2 for "today", decays over a year
    days = max(0, (datetime.utcnow() - published).days)
    recency = max(0.0, 0.2 - (days / 365.0) * 0.2)
    caution_penalty = -0.1 if caution else 0.0
    return round(type_weight + peer + size + recency + caution_penalty, 3)
