# UI Component Extractor

A high-performance, asynchronous web crawler designed to map out website structures and extract raw HTML snippets of UI components for easy reuse and analysis. Built with `asyncio`, `aiohttp`, and `BeautifulSoup4`.

## Features (4 Distinct Modes)

When you run the crawler, you can choose from 4 specialized data extraction engines:

1. **Classic Links Mapper**: Extracts basic internal links alongside their UI text and tooltips (`title`/`aria-label`).
2. **UI Component Extractor**: Steals styling! Grabs the raw HTML snippet and inline CSS/classes of UI components. The generated report includes **syntax highlighting** (powered by `highlight.js`) so the code is easy to read.
3. **Audio & Stream Hunter**: Scans the website strictly for audio assets (`.mp3`, `.wav`, `.m3u8` streams, `<audio>`, `<source>`). Great for ripping media.
4. **SEO & Meta Auditor**: Instead of extracting links, it pulls the `<title>`, `<meta description>`, and OpenGraph (`og:image`) tags from every page it crawls, generating a full SEO health audit.

### Core Architecture
- **🚀 Asynchronous Turbo Crawling**: Utilizes `aiohttp` and `lxml` to process dozens of pages concurrently, offering massive speed improvements over synchronous scrapers.
- **📊 Minimalist HTML Reports**: Generates a sleek, auto-opening HTML report with a clean table view powered by the Inter font.
- **🔄 Smart Redirect & Domain Handling**: Follows server redirects and automatically matches root domains to avoid breaking on subdomains like `www.`.
- **🛡️ Bot-Protection Awareness**: Detects and flags non-200 HTTP responses (e.g., 403 Forbidden or 429 Too Many Requests) with color-coded terminal alerts.

## Requirements

- Python 3.8+
- `aiohttp`
- `beautifulsoup4`
- `lxml`

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/niktoimiyazap/ui-component-extractor.git
cd ui-component-extractor
pip install -r requirements.txt
```

## Usage

Simply run the script. It operates in an interactive mode:

```bash
python3 crawler.py
```

1. **Enter the URL**: e.g., `example.com` or `https://example.com`
2. **Set a limit**: Enter the maximum number of links to discover, or press `Enter` to crawl infinitely.

The crawler will output its progress in real-time with color-coded terminal messages. Once completed (or upon pressing `Ctrl+C`), it will automatically compile the extracted data and open `report.html` in your default web browser.

## Example Report
The generated `report.html` provides a scrollable, modern interface where you can view:
- The URL
- The extracted UI text
- Tooltip metadata
- **Component HTML**: The raw, copy-pasteable HTML of the UI element and its inline classes/styles.

## Disclaimer

This tool is strictly intended for educational purposes, personal UI inspiration, and structural analysis. Please respect `robots.txt` and the terms of service of the websites you crawl.
