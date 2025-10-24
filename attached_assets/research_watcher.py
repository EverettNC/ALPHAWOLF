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
research_watcher.py
Scaffold for fetching and curating new Alzheimer's/dementia research.
Integrate with AlphaWolf by calling `get_digest()` for the top items.
Uses pluggable fetchers. Start with PubMed/NIH/Cochrane via official APIs or RSS.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# NOTE: This scaffold avoids network calls so it can run offline.
# Implement the actual HTTP calls in `fetchers/pubmed.py` etc. using requests/httpx.

@dataclass
class Paper:
    id: str
    title: str
    abstract: str
    url: str
    source: str             # 'pubmed' | 'nia' | 'cochrane' | 'medrxiv' | 'alz_org'
    published: datetime
    study_type: str         # 'rct' | 'cohort' | 'meta_analysis' | 'systematic_review' | 'case_report' | 'guideline'
    peer_reviewed: bool
    sample_size: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    caution: Optional[str] = None

def quality_score(p: Paper) -> float:
    # Simple scoring heuristic; tune later.
    type_weight = {
        'meta_analysis': 1.0,
        'systematic_review': 0.95,
        'rct': 0.9,
        'cohort': 0.7,
        'guideline': 0.6,
        'case_report': 0.3,
    }.get(p.study_type, 0.5)
    peer = 0.1 if p.peer_reviewed else -0.15
    size = 0.0 if not p.sample_size else min(0.2, p.sample_size / 5000.0 * 0.2)
    recency = max(0.0, 0.2 - (datetime.utcnow() - p.published).days / 365.0 * 0.2)
    caution = -0.1 if p.caution else 0.0
    return round(type_weight + peer + size + recency + caution, 3)

def curate(papers: List[Paper]) -> List[Paper]:
    # De-duplicate by id, score, and keep top per tag
    uniq: Dict[str, Paper] = {}
    for p in papers:
        p.quality_score = quality_score(p)
        if p.id not in uniq or p.quality_score > uniq[p.id].quality_score:
            uniq[p.id] = p
    ranked = sorted(uniq.values(), key=lambda x: (x.quality_score, x.published), reverse=True)
    return ranked

def get_digest(papers: List[Paper], n: int = 3) -> List[Dict]:
    top = curate(papers)[:n]
    digest = []
    for p in top:
        digest.append({
            "title": p.title,
            "takeaway": summarize_takeaway(p),   # implement with your LLM + citations
            "strength": strength_label(p.quality_score),
            "url": p.url,
            "source": p.source,
            "published": p.published.isoformat(),
            "tags": p.tags,
            "caution": p.caution
        })
    return digest

def strength_label(score: float) -> str:
    if score >= 1.0: return "strong"
    if score >= 0.8: return "good"
    if score >= 0.6: return "moderate"
    return "preliminary"

def summarize_takeaway(p: Paper) -> str:
    # Placeholder. Replace with retrieval-augmented summarization and force citations.
    return f"{p.study_type} suggests potential impact; verify in source. (score={p.quality_score})"

if __name__ == "__main__":
    # Offline demo
    now = datetime.utcnow()
    sample = [
        Paper(id="demo1", title="Music therapy and agitation in dementia",
              abstract="...", url="https://example.org/demo1", source="cochrane",
              published=now - timedelta(days=10), study_type="systematic_review",
              peer_reviewed=True, sample_size=1200, tags=["music", "agitation"]),
        Paper(id="demo2", title="Sleep hygiene in mild cognitive impairment",
              abstract="...", url="https://example.org/demo2", source="nia",
              published=now - timedelta(days=25), study_type="cohort",
              peer_reviewed=True, sample_size=400, tags=["sleep"]),
        Paper(id="demo3", title="Novel wandering predictors",
              abstract="...", url="https://example.org/demo3", source="medrxiv",
              published=now - timedelta(days=5), study_type="rct",
              peer_reviewed=False, sample_size=90, tags=["wandering"], caution="preprint"),
    ]
    from pprint import pprint
    pprint(get_digest(sample))
