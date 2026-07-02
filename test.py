import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import sys

def get_base_domain(url):
    netloc = urlparse(url).netloc
    if netloc.startswith("www."):
        return netloc[4:]
    return netloc

async def test_get(url):
    domain_name = get_base_domain(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=10, ssl=False) as response:
            print("Status:", response.status)
            html = await response.text()
            soup = BeautifulSoup(html, "lxml")
            actual_url = str(response.url)
            print("Actual URL:", actual_url)
            
            links = soup.find_all("a")
            print("Found a_tags count:", len(links))
            for a_tag in links:
                href = a_tag.attrs.get("href")
                if not href: continue
                href = urljoin(actual_url, href)
                parsed_href = urlparse(href)
                href = f"{parsed_href.scheme}://{parsed_href.netloc}{parsed_href.path}"
                print(f"Href: {href} | Base domain: {get_base_domain(href)} | Domain Name: {domain_name}")
                if domain_name not in get_base_domain(href):
                    print("  -> SKIPPED (domain mismatch)")

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(test_get("https://google.com/"))
