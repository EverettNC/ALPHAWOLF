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

