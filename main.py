import sys
import asyncio
from omnicrawl.crawler import crawl

def main():
    print("=== OmniCrawl ===")
    print("Select an extraction mode:")
    print("  1) Classic Links (URL, Text, Tooltips)")
    print("  2) UI Components (HTML Snippets + Interactive Sandbox)")
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
        print("\n\033[91m[!] OmniCrawl interrupted by user.\033[0m")
        sys.exit(0)

if __name__ == "__main__":
    main()
