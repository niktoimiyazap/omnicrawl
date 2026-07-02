import sys
import asyncio
from omnicrawl.crawler import crawl

def run_cli():
    print(r"""
   ____                  _ ______                    __
  / __ \____ ___  ____  (_) ____/________ __      __/ /
 / / / / __ `__ \/ __ \/ / /   / ___/ __ `/ | /| / / / 
/ /_/ / / / / / / / / / / /___/ /  / /_/ /| |/ |/ / /  
\____/_/ /_/ /_/_/ /_/_/\____/_/   \__,_/ |__/|__/_/   
                                                v1.0.0
    """)
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
        
    max_input = input("Enter the maximum number of pages to crawl (leave empty for infinite): ").strip()
    try:
        max_urls = int(max_input) if max_input else 1000000
    except ValueError:
        print("\033[91m[-] Invalid number. Defaulting to 40.\033[0m")
        max_urls = 40
        
    stay_domain_input = input("Stay within the original domain? (Y/n): ").strip().lower()
    stay_in_domain = False if stay_domain_input == 'n' else True
        
    try:
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(crawl(start_url, max_urls=max_urls, mode=mode, stay_in_domain=stay_in_domain))
    except KeyboardInterrupt:
        print("\n\033[91m[!] OmniCrawl interrupted by user. Generating partial report...\033[0m")
        sys.exit(0)
