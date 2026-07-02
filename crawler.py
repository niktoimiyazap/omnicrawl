import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import sys
import os
import webbrowser
import html

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

def generate_html_report(domain_name, collected_data, mode):
    report_path = os.path.abspath("report.html")
    
    # Mode-specific table headers and scripts
    extra_head = ""
    if mode == 1:
        mode_name = "Classic Links Mapper"
        headers = ["URL", "Link Text", "Tooltip"]
    elif mode == 2:
        mode_name = "UI Component Extractor"
        headers = ["URL", "Link Text", "Component HTML (UI)"]
        # Add highlight.js for syntax highlighting
        extra_head = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <script>document.addEventListener('DOMContentLoaded', (event) => { document.querySelectorAll('pre code').forEach((el) => { hljs.highlightElement(el); }); });</script>
        """
    elif mode == 3:
        mode_name = "Audio & Stream Hunter"
        headers = ["Media URL", "Element Type", "Context / Text"]
    elif mode == 4:
        mode_name = "SEO & Meta Auditor"
        headers = ["Page URL", "Title", "Meta Description", "OG Image"]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crawler Report - {domain_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background: #f9fafb; color: #111827; padding: 2rem; margin: 0; }}
        h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; font-weight: 600; }}
        h2 {{ font-size: 1rem; margin-bottom: 1.5rem; font-weight: 400; color: #4b5563; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #e5e7eb; font-size: 0.875rem; vertical-align: top; }}
        th {{ background: #f3f4f6; font-weight: 600; color: #374151; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover {{ background: #f9fafb; }}
        a {{ color: #2563eb; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        pre {{ margin: 0; max-width: 500px; max-height: 200px; overflow: auto; border-radius: 4px; font-size: 12px; }}
        img.og-preview {{ max-width: 150px; border-radius: 4px; border: 1px solid #e5e7eb; }}
    </style>{extra_head}
</head>
<body>
    <h1>Crawler Report: {domain_name}</h1>
    <h2>Mode: {mode_name} | Total Items: {len(collected_data)}</h2>
    <table>
        <thead>
            <tr>
"""
    for header in headers:
        html_content += f"                <th>{header}</th>\n"
        
    html_content += """            </tr>
        </thead>
        <tbody>
"""

    for key, info in sorted(collected_data.items()):
        html_content += "            <tr>\n"
        if mode == 1:
            html_content += f"""                <td><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td>{info['text']}</td>
                <td>{info['tooltip']}</td>\n"""
        elif mode == 2:
            html_content += f"""                <td><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td>{info['text']}</td>
                <td><pre><code class="language-html">{info['html']}</code></pre></td>\n"""
        elif mode == 3:
            html_content += f"""                <td><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td><span style="background: #e5e7eb; padding: 2px 6px; border-radius: 4px;">{info['type']}</span></td>
                <td>{info['context']}</td>\n"""
        elif mode == 4:
            img_tag = f'<img src="{info["og_image"]}" class="og-preview">' if info["og_image"] else "No Image"
            html_content += f"""                <td><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td><strong>{info['title']}</strong></td>
                <td>{info['description']}</td>
                <td>{img_tag}</td>\n"""
        html_content += "            </tr>\n"

    html_content += """        </tbody>
    </table>
</body>
</html>"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"\n\033[92m[+] Report saved to {report_path}\033[0m")
    
    try:
        if sys.platform == 'darwin':
            os.system(f'open "{report_path}"')
        else:
            webbrowser.open(f"file://{report_path}")
    except Exception as e:
        print(f"\033[91m[-] Could not open browser automatically. Please open the file manually: {report_path}\033[0m")

async def crawl(start_url, max_urls, mode):
    print(f"\n[*] Starting crawl for: {start_url}")
    print(f"[*] Maximum URLs to discover: {max_urls}")
    
    domain_name = get_base_domain(start_url)
    visited_urls = {start_url}
    to_visit = {start_url}
    
    collected_data = {}
    semaphore = asyncio.Semaphore(50)

    async def fetch_and_parse(session, url):
        async with semaphore:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            try:
                async with session.get(url, headers=headers, timeout=10, ssl=False) as response:
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
        while to_visit and len(visited_urls) < max_urls:
            tasks = [fetch_and_parse(session, url) for url in to_visit]
            to_visit = set()
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for res in results:
                if isinstance(res, Exception) or not isinstance(res, tuple):
                    continue
                    
                req_url, soup, actual_url = res
                if not soup:
                    continue
                
                # 1. Discover internal links for the crawler queue
                for a_tag in soup.find_all("a"):
                    href = a_tag.attrs.get("href")
                    if not href: continue
                    href = urljoin(actual_url, href)
                    parsed = urlparse(href)
                    href = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    
                    if is_valid_url(href) and domain_name in get_base_domain(href):
                        if href not in visited_urls and len(visited_urls) < max_urls:
                            visited_urls.add(href)
                            to_visit.add(href)
                
                # 2. Extract Data based on Mode
                if mode in (1, 2):
                    for a_tag in soup.find_all("a"):
                        href = a_tag.attrs.get("href")
                        if not href: continue
                        href = urljoin(actual_url, href)
                        parsed = urlparse(href)
                        href = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                        
                        if href not in collected_data:
                            link_text = a_tag.get_text(strip=True)
                            if not link_text:
                                img = a_tag.find("img")
                                if img and img.attrs.get("alt"):
                                    link_text = img.attrs.get("alt").strip()
                                    
                            tooltip = a_tag.attrs.get("title", "").strip()
                            if not tooltip:
                                tooltip = a_tag.attrs.get("aria-label", "").strip()
                                
                            link_text = " ".join(link_text.split())
                            tooltip = " ".join(tooltip.split())
                            
                            info = {'url': href, 'text': link_text, 'tooltip': tooltip}
                            
                            if mode == 2:
                                parent = a_tag.parent
                                parent_html = str(parent) if parent else str(a_tag)
                                if len(parent_html) > 1500: parent_html = str(a_tag)
                                info['html'] = html.escape(parent_html)
                                
                            collected_data[href] = info
                            print(f"\033[92m[+] Discovered UI Element: {href}\033[0m")
                            
                elif mode == 3:
                    audio_tags = soup.find_all(["audio", "source", "a"])
                    for tag in audio_tags:
                        src = tag.attrs.get("src") or tag.attrs.get("href")
                        if not src: continue
                        
                        is_audio = False
                        if tag.name == "audio":
                            is_audio = True
                        elif tag.name == "source" and "audio" in tag.attrs.get("type", ""):
                            is_audio = True
                        elif src.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.m3u8')):
                            is_audio = True
                            
                        if is_audio:
                            full_src = urljoin(actual_url, src)
                            if full_src not in collected_data:
                                context = tag.parent.get_text(strip=True)[:100] if tag.parent else ""
                                collected_data[full_src] = {'url': full_src, 'type': tag.name, 'context': context}
                                print(f"\033[92m[+] Discovered Audio: {full_src}\033[0m")
                                
                elif mode == 4:
                    if actual_url not in collected_data:
                        title = soup.title.string.strip() if soup.title and soup.title.string else ""
                        desc_tag = soup.find("meta", attrs={"name": "description"})
                        desc = desc_tag.attrs.get("content", "").strip() if desc_tag else ""
                        og_image_tag = soup.find("meta", attrs={"property": "og:image"})
                        og_image = og_image_tag.attrs.get("content", "").strip() if og_image_tag else ""
                        
                        collected_data[actual_url] = {
                            'url': actual_url,
                            'title': title,
                            'description': desc,
                            'og_image': og_image
                        }
                        print(f"\033[92m[+] Audited Page: {actual_url}\033[0m")

    print(f"\n\033[92m[+] Total items collected: {len(collected_data)}\033[0m")
    generate_html_report(domain_name, collected_data, mode)

def main():
    print("=== Universal Web Crawler ===")
    print("Select an extraction mode:")
    print("  1) Classic Links (URL, Text, Tooltips)")
    print("  2) UI Components (HTML Snippets with Syntax Highlighting)")
    print("  3) Audio & Stream Hunter (.mp3, .m3u8, <audio> tags)")
    print("  4) SEO & Meta Auditor (Titles, Descriptions, OpenGraph Images)")
    
    while True:
        mode_input = input("\nEnter mode (1-4): ").strip()
        if mode_input in ('1', '2', '3', '4'):
            mode = int(mode_input)
            break
        print("\033[91mError: Please enter a valid number (1, 2, 3, or 4).\033[0m")
        
    start_url = input("\nEnter the URL to crawl (e.g., example.com): ").strip()
    if not start_url:
        print("\033[91mError: URL cannot be empty.\033[0m")
        sys.exit(1)
        
    if not start_url.startswith("http://") and not start_url.startswith("https://"):
        start_url = "https://" + start_url
        
    max_urls_input = input("Enter the maximum number of pages to crawl (leave empty for infinite): ").strip()
    if max_urls_input.isdigit():
        max_urls = int(max_urls_input)
    else:
        max_urls = 1000000
        
    try:
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(crawl(start_url, max_urls=max_urls, mode=mode))
    except KeyboardInterrupt:
        print("\n\033[91m[!] Crawl interrupted by user.\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()
