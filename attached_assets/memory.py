import json
import os
from cryptography.fernet import Fernet

# Directory and file setup
MEMORY_DIR = "ai"
MEMORY_FILE = os.path.join(MEMORY_DIR, "memory.json")
KEY_FILE = os.path.join(MEMORY_DIR, "secret.key")

os.makedirs(MEMORY_DIR, exist_ok=True)

# Generate encryption key if missing
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(Fernet.generate_key())

with open(KEY_FILE, "rb") as f:
    fernet = Fernet(f.read())


def save_memory(data):
    """Encrypt and save memory data to file."""
    with open(MEMORY_FILE, "wb") as f:
        f.write(fernet.encrypt(json.dumps(data).encode()))


def load_memory():
    """Load and decrypt memory data, or return defaults if missing."""
    if not os.path.exists(MEMORY_FILE):
        return {"users": {}}
    with open(MEMORY_FILE, "rb") as f:
        return json.loads(fernet.decrypt(f.read()))
