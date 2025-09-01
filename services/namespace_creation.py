# utils/namespace_creation.py
import os
import re
from datetime import datetime

def generate_namespace(filename: str, num_words: int = 3) -> str:
    """
    Generate a Pinecone-compatible namespace from a filename.
    
    Rules:
    - Take first `num_words` from the filename (excluding extension).
    - Append current time (HHMMSS).
    - Allow only letters, numbers, and hyphens.
    - Convert to lowercase.
    """

    # Extract base filename (without extension)
    base_name = os.path.splitext(filename)[0]

    # Take first few words
    words = base_name.replace("_", " ").replace("-", " ").split()
    prefix = "-".join(words[:num_words]) if words else "file"

    # Add current time
    time_str = datetime.now().strftime("%H%M%S")
    raw_namespace = f"{prefix}-{time_str}"

    # Sanitize: keep only letters, numbers, hyphens
    namespace = re.sub(r"[^a-zA-Z0-9-]", "-", raw_namespace)

    return namespace.lower()
