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
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import base64
import os

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = "everettc"
REPO = "derek-dashboard"

router = APIRouter()


class GitHubFile(BaseModel):
    path: str
    content: str  # raw content
    message: str
    sha: Optional[str] = None


HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


@router.put("/memory/save")
async def save_to_memory(file: GitHubFile):
    """Save a file to the GitHub repository at the given path."""
    url = f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/{file.path}"
    payload = {
        "message": file.message,
        "content": base64.b64encode(file.content.encode()).decode(),
    }
    if file.sha:
        payload["sha"] = file.sha

    async with httpx.AsyncClient() as client:
        r = await client.put(url, headers=HEADERS, json=payload)
        if r.status_code not in (200, 201):
            raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()


@router.get("/memory/load")
async def load_from_memory(path: str):
    """Load a file from the GitHub repository by path."""
    url = f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/{path}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=HEADERS)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        raw = r.json()
        content = base64.b64decode(raw.get("content", "")).decode()
        return {"path": path, "content": content, "sha": raw.get("sha")}


@router.put("/reflection/save")
async def save_reflection(file: GitHubFile):
    """Save a reflection markdown file under memory/reflections/ on GitHub."""
    file.path = f"memory/reflections/{file.path}"
    return await save_to_memory(file)


@router.get("/reflection/load")
async def load_reflection(date: str):
    """Load a reflection markdown file for a given date from GitHub."""
    path = f"memory/reflections/{date}.md"
    return await load_from_memory(path)
