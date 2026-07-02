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
    print("  1) General Links & Navigation (URLs, Text, Tooltips)")
    print("  2) UI Elements & Components (HTML/CSS Snippets + Sandbox)")
    print("  3) Audio & Video Streams (.mp3, .m3u8, <audio>, <video>)")
    print("  4) Metadata & Media (SEO, Images, GIFs, Animations)")
    
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
        
    max_pages_input = input("Enter the maximum number of PAGES to crawl (leave empty for infinite): ").strip()
    try:
        max_pages = int(max_pages_input) if max_pages_input else 1000000
    except ValueError:
        print("\033[91m[-] Invalid number. Defaulting to 40.\033[0m")
        max_pages = 40
        
    max_items_input = input("Enter the maximum number of ITEMS to extract (leave empty for infinite): ").strip()
    try:
        max_items = int(max_items_input) if max_items_input else 1000000
    except ValueError:
        print("\033[91m[-] Invalid number. Defaulting to 100.\033[0m")
        max_items = 100
        
    stay_domain_input = input("Stay within the original domain? (Y/n): ").strip().lower()
    stay_in_domain = False if stay_domain_input == 'n' else True
        
    try:
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(crawl(start_url, max_pages=max_pages, max_items=max_items, mode=mode, stay_in_domain=stay_in_domain))
    except KeyboardInterrupt:
        print("\n\033[91m[!] OmniCrawl interrupted by user. Generating partial report...\033[0m")
        sys.exit(0)
