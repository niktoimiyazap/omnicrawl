import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import sys

def is_valid_url(url):
    """Check if the URL is valid."""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

async def get_all_website_links(session, url, domain_name):
    """Returns all URLs that are found on `url` and belong to the same website."""
    urls = set()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status != 200:
                return set()
            html = await response.text()
            # lxml is significantly faster than html.parser
            soup = BeautifulSoup(html, "lxml")
    except Exception as e:
        print(f"[-] Ошибка доступа {url}: {e}", file=sys.stderr)
        return set()

    for a_tag in soup.find_all("a"):
        href = a_tag.attrs.get("href")
        if not href:
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

async def crawl(start_url, max_urls):
    """Crawls a website asynchronously."""
    print(f"[*] Старт турбо-парсинга: {start_url}")
    print(f"[*] Максимум ссылок: {max_urls}\n")
    
    domain_name = urlparse(start_url).netloc
    visited = {start_url}
    to_visit = {start_url}
    
    # Limit concurrent requests to avoid getting banned or crashing
    semaphore = asyncio.Semaphore(50)

    async def fetch_and_parse(session, url):
        async with semaphore:
            return await get_all_website_links(session, url, domain_name)

    # Use a TCPConnector to limit total connections if needed, but aiohttp defaults to 100
    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        while to_visit and len(visited) < max_urls:
            # Create a batch of tasks for the current breadth level
            tasks = [fetch_and_parse(session, url) for url in to_visit]
            to_visit = set()
            
            # Execute all tasks in this level concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for links in results:
                if isinstance(links, set):
                    for link in links:
                        if link not in visited and len(visited) < max_urls:
                            visited.add(link)
                            to_visit.add(link)
                            print(f"[*] Найдено ({len(visited)}): {link}")
                            if len(visited) >= max_urls:
                                break

    print(f"\n[+] Всего уникальных внутренних ссылок найдено: {len(visited)}")
    print("=" * 50)
    for url in sorted(visited):
        print(url)
    print("=" * 50)

def main():
    print("=== Добро пожаловать в Site Crawler (ASYNC TURBO) ===")
    start_url = input("Введите ссылку для парсинга (например, example.com): ").strip()
    
    if not start_url:
        print("Ошибка: Ссылка не может быть пустой.")
        sys.exit(1)
        
    if not start_url.startswith("http://") and not start_url.startswith("https://"):
        start_url = "https://" + start_url
        
    max_urls_input = input("Сколько ссылок парсить? (Оставьте пустым для 'бесконечного' парсинга, или введите число): ").strip()
    
    if max_urls_input.isdigit():
        max_urls = int(max_urls_input)
    else:
        max_urls = 1000000
        
    try:
        # For Windows compatibility with aiohttp (ProactorEventLoop)
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(crawl(start_url, max_urls=max_urls))
    except KeyboardInterrupt:
        print("\n[!] Парсинг остановлен пользователем.")
        sys.exit(0)

if __name__ == "__main__":
    main()
