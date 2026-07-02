from urllib.parse import urlparse

def get_base_domain(url):
    """Get the base domain without www."""
    netloc = urlparse(url).netloc
    if netloc.startswith("www."):
        return netloc[4:]
    return netloc

def is_valid_url(url):
    """Check if the URL is valid."""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)
