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
import re

# Basic keywords mapped to emotions
tags_map = {
    "love": "emotional",
    "angry": "frustration",
    "sad": "loss",
    "tired": "fatigue",
    "build": "momentum",
    "vision": "strategic",
    "plan": "strategic",
    "fuck": "intensity",
    "baby": "bonding",
    "you": "relational",
    "alone": "isolation",
    "fire": "drive",
    "voice": "identity"
}

MEMORY_PATH = "derek_memory.json"


def tag_emotions():
    try:
        with open(MEMORY_PATH, "r") as f:
            memory = json.load(f)
    except FileNotFoundError:
        return []

    updated = []
    for entry in memory:
        combined = f"{entry['input']} {entry['response']}".lower()
        tags = set()
        for word, emotion in tags_map.items():
            if re.search(rf"\\b{word}\\b", combined):
                tags.add(emotion)
        entry["tags"] = list(tags)
        updated.append(entry)

    with open(MEMORY_PATH, "w") as f:
        json.dump(updated, f, indent=2)

    return updated


if __name__ == "__main__":
    result = tag_emotions()
    print(f"Tagged {len(result)} memories with emotional context.")

