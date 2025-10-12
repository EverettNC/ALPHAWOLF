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
