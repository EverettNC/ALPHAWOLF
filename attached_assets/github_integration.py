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
"""GitHub integration helpers for Derek Dashboard API."""

import logging
from typing import Dict, Any

from config.settings import Settings

try:
    from github import Github  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Github = None

logger = logging.getLogger(__name__)


def get_repository_metadata() -> Dict[str, Any]:
    """Fetch repository metadata using PyGithub if available."""
    settings = Settings()
    token = settings.GITHUB_TOKEN
    repo_name = settings.GITHUB_REPO

    if Github is None or not token:
        logger.warning("GitHub integration unavailable; provide GITHUB_TOKEN")
        return {"repository": repo_name, "available": False}

    client = Github(token)
    repo = client.get_repo(repo_name)
    return {
        "repository": repo.full_name,
        "stars": repo.stargazers_count,
        "open_issues": repo.open_issues_count,
    }
