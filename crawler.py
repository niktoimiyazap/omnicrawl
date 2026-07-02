import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import sys
import os
import webbrowser

def is_valid_url(url):
    """Check if the URL is valid."""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

async def get_all_website_links(session, url, domain_name):
    """Returns a dict of URLs and their UI metadata (text, tooltip) found on `url`."""
    urls_info = {}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # ssl=False prevents CERTIFICATE_VERIFY_FAILED errors on some environments like macOS
        async with session.get(url, headers=headers, timeout=10, ssl=False) as response:
            if response.status != 200:
                return {}
            html = await response.text()
            soup = BeautifulSoup(html, "lxml")
    except Exception as e:
        print(f"\033[91m[-] Error accessing {url}: {e}\033[0m", file=sys.stderr)
        return {}

    for a_tag in soup.find_all("a"):
        href = a_tag.attrs.get("href")
        if not href:
            continue
        
        # Get text from the link
        link_text = a_tag.get_text(strip=True)
        if not link_text:
            # Fallback to image alt text if available
            img = a_tag.find("img")
            if img and img.attrs.get("alt"):
                link_text = img.attrs.get("alt").strip()
                
        # Get tooltip (title or aria-label)
        tooltip = a_tag.attrs.get("title", "").strip()
        if not tooltip:
            tooltip = a_tag.attrs.get("aria-label", "").strip()
            
        # Clean up line breaks for output
        link_text = " ".join(link_text.split())
        tooltip = " ".join(tooltip.split())
        
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
            
        # Save link metadata (keep the first occurrence)
        if href not in urls_info:
            urls_info[href] = {
                'text': link_text,
                'tooltip': tooltip
            }
        
    return urls_info

async def crawl(start_url, max_urls):
    """Crawls a website asynchronously."""
    print(f"[*] Starting crawl for: {start_url}")
    print(f"[*] Maximum URLs to discover: {max_urls}\n")
    
    domain_name = urlparse(start_url).netloc
    
    visited = {start_url: {'text': 'Root URL', 'tooltip': ''}}
    to_visit = {start_url}
    
    semaphore = asyncio.Semaphore(50)

    async def fetch_and_parse(session, url):
        async with semaphore:
            return await get_all_website_links(session, url, domain_name)

    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        while to_visit and len(visited) < max_urls:
            tasks = [fetch_and_parse(session, url) for url in to_visit]
            to_visit = set()
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for url_infos in results:
                if isinstance(url_infos, dict):
                    for link, info in url_infos.items():
                        if link not in visited and len(visited) < max_urls:
                            visited[link] = info
                            to_visit.add(link)
                            
                            # Format the output log
                            text_out = f" | Text: '{info['text']}'" if info['text'] else ""
                            tooltip_out = f" | Tooltip: '{info['tooltip']}'" if info['tooltip'] else ""
                            print(f"[*] Discovered ({len(visited)}): {link}{text_out}{tooltip_out}")
                            
                            if len(visited) >= max_urls:
                                break

    print(f"\n[+] Total unique internal links found: {len(visited)}")
    
    # Generate HTML report
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crawler Report - {domain_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background: #f9fafb; color: #111827; padding: 2rem; margin: 0; }}
        h1 {{ font-size: 1.5rem; margin-bottom: 1rem; font-weight: 600; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #e5e7eb; font-size: 0.875rem; }}
        th {{ background: #f3f4f6; font-weight: 600; color: #374151; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover {{ background: #f9fafb; }}
        a {{ color: #2563eb; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Crawler Report: {domain_name} ({len(visited)} links)</h1>
    <table>
        <thead>
            <tr>
                <th>URL</th>
                <th>Link Text</th>
                <th>Tooltip</th>
            </tr>
        </thead>
        <tbody>
"""
    for url, info in sorted(visited.items()):
        html_content += f"""            <tr>
                <td><a href="{url}" target="_blank">{url}</a></td>
                <td>{info['text']}</td>
                <td>{info['tooltip']}</td>
            </tr>\n"""
            
    html_content += """        </tbody>
    </table>
</body>
</html>"""

    report_path = os.path.abspath("report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[*] Report saved to {report_path}")
    webbrowser.open(f"file://{report_path}")

def main():
    print("=== Site Crawler ===")
    start_url = input("Enter the URL to crawl (e.g., example.com): ").strip()
    
    if not start_url:
        print("\033[91mError: URL cannot be empty.\033[0m")
        sys.exit(1)
        
    if not start_url.startswith("http://") and not start_url.startswith("https://"):
        start_url = "https://" + start_url
        
    max_urls_input = input("Enter the maximum number of links to discover (leave empty for infinite): ").strip()
    
    if max_urls_input.isdigit():
        max_urls = int(max_urls_input)
    else:
        max_urls = 1000000
        
    try:
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(crawl(start_url, max_urls=max_urls))
    except KeyboardInterrupt:
        print("\n\033[91m[!] Crawl interrupted by user.\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()
