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
import requests


def check_internet_access(url):
    """
    Checks if a URL is accessible and prints the response status.
    """
    try:
        # Add headers to mimic a web browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }

        # Send the request with the new headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)

        print(f"Successfully accessed {url}. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to access {url}. Error: {e}")


# Example usage:
check_internet_access("https://openai.com/blog")
