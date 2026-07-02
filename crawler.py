import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from collections import deque
import sys

def is_valid_url(url):
    """Check if the URL is valid."""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url):
    """Returns all URLs that are found on `url` and belong to the same website."""
    urls = set()
    domain_name = urlparse(url).netloc
    
    # Use headers to mimic a regular browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"[-] Error accessing {url}: {e}", file=sys.stderr)
        return set()

    for a_tag in soup.find_all("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            continue
        
        # Resolve relative URLs
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        
        # Remove URL fragments and query parameters for clean links
        href = f"{parsed_href.scheme}://{parsed_href.netloc}{parsed_href.path}"
        
        if not is_valid_url(href):
            continue
        
        # Check if the URL is internal (same domain)
        if domain_name not in href:
            continue
            
        urls.add(href)
        
    return urls

def crawl(start_url, max_urls=50):
    """Crawls a website starting from a given URL up to max_urls."""
    print(f"[*] Starting crawl for: {start_url}")
    print(f"[*] Maximum URLs to discover: {max_urls}\n")
    
    visited = set()
    queue = deque([start_url])
    
    while queue and len(visited) < max_urls:
        current_url = queue.popleft()
        
        if current_url in visited:
            continue
            
        print(f"[*] Crawling: {current_url}")
        visited.add(current_url)
        
        links = get_all_website_links(current_url)
        for link in links:
            if link not in visited and link not in queue:
                queue.append(link)
                
    print(f"\n[+] Total unique internal links found: {len(visited)}")
    print("=" * 40)
    for url in sorted(visited):
        print(url)
    print("=" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple web crawler to map out internal links of a website.")
    parser.add_argument("url", help="The starting URL to crawl (e.g., example.com or https://example.com)")
    parser.add_argument("-m", "--max-urls", help="Maximum number of URLs to crawl (default: 50)", type=int, default=50)
    args = parser.parse_args()
    
    start_url = args.url
    if not start_url.startswith("http://") and not start_url.startswith("https://"):
        start_url = "https://" + start_url
        
    crawl(start_url, max_urls=args.max_urls)
