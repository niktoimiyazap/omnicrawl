import asyncio
import aiohttp
import sys
from bs4 import BeautifulSoup
from omnicrawl.constants import HEADERS
from omnicrawl.utils import get_base_domain
from omnicrawl.parser import extract_internal_links, parse_page_data
from omnicrawl.report import generate_html_report

async def crawl(start_url, max_urls, mode, stay_in_domain=True):
    print(f"\n[*] Starting OmniCrawl for: {start_url}")
    print(f"[*] Maximum URLs to discover: {max_urls}")
    print(f"[*] Stay in Domain: {stay_in_domain}")
    
    domain_name = get_base_domain(start_url)
    visited_urls = {start_url}
    to_visit = {start_url}
    
    collected_data = {}
    semaphore = asyncio.Semaphore(50)

    async def fetch_and_parse(session, url):
        async with semaphore:
            print(f"[*] Fetching: {url}")
            try:
                async with session.get(url, headers=HEADERS, timeout=10, ssl=False) as response:
                    if response.status != 200:
                        print(f"\033[93m[!] HTTP {response.status} for {url} (Bot protection?)\033[0m", file=sys.stderr)
                        return url, None, str(response.url)
                    html_text = await response.text()
                    soup = BeautifulSoup(html_text, "lxml")
                    return url, soup, str(response.url)
            except Exception as e:
                print(f"\033[91m[-] Error accessing {url}: {e}\033[0m", file=sys.stderr)
                return url, None, ""

    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        fetched_count = 0
        while to_visit and fetched_count < max_urls:
            # Only take enough URLs from to_visit to reach max_urls
            batch = list(to_visit)[:max_urls - fetched_count]
            to_visit = set(list(to_visit)[len(batch):])
            
            tasks = [fetch_and_parse(session, url) for url in batch]
            fetched_count += len(batch)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for res in results:
                if isinstance(res, Exception) or not isinstance(res, tuple):
                    continue
                    
                req_url, soup, actual_url = res
                if not soup:
                    continue
                
                # 1. Discover internal links for the crawler queue
                new_links = extract_internal_links(soup, actual_url, domain_name, stay_in_domain)
                for href in new_links:
                    if href not in visited_urls:
                        visited_urls.add(href)
                        to_visit.add(href)
                
                # 2. Extract Data based on Mode
                parse_page_data(mode, soup, actual_url, collected_data)

    print(f"\n\033[92m[+] Total items collected: {len(collected_data)}\033[0m")
    generate_html_report(domain_name, collected_data, mode)
