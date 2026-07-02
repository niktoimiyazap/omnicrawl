# Simple Web Crawler

A straightforward Python script that parses a given website URL from the terminal and collects all internal links/branches of that site. It uses Breadth-First Search (BFS) to map out the pages belonging to the same domain.

## Requirements

- Python 3.6+
- `requests`
- `beautifulsoup4`

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/niktoimiyazap/site-crawler.git
cd site-crawler
pip install -r requirements.txt
```

## Usage

Run the script from your terminal by providing the starting URL:

```bash
python crawler.py example.com
```

You can optionally specify the maximum number of URLs to crawl using the `-m` or `--max-urls` flag (default is 50):

```bash
python crawler.py https://example.com -m 100
```

## Example Output

```text
[*] Starting crawl for: https://example.com
[*] Maximum URLs to discover: 50

[*] Crawling: https://example.com
[*] Crawling: https://example.com/about
[*] Crawling: https://example.com/contact

[+] Total unique internal links found: 3
========================================
https://example.com
https://example.com/about
https://example.com/contact
========================================
```

## Disclaimer

This tool is intended for educational purposes and personal use. Please respect website policies and `robots.txt` when crawling.
