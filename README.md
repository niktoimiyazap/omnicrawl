<h1 align="center">
  OmniCrawl
</h1>

<p align="center">
  <strong>A Universal, High-Performance Asynchronous Web Extraction Framework</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/asyncio-enabled-success.svg" alt="Asyncio">
  <img src="https://img.shields.io/badge/release-v1.0.0-green.svg" alt="Release">
</p>

OmniCrawl is an incredibly fast, multi-mode web scraper built with `aiohttp` and `asyncio`. It crawls deep into websites to extract everything from basic links and SEO meta tags to raw UI components (complete with CSS) and media files.

## 🚀 Features

- **Blazing Fast**: Asynchronous I/O using `aiohttp` and a bounded semaphore allows fetching 100s of pages concurrently.
- **Cross-Domain Wandering**: Toggle between strict domain locking and infinite cross-domain web wandering.
- **Four Specialized Modes**:
  - **1) Classic Links**: Extracts all internal URLs, link text, and tooltips.
  - **2) UI Component Extractor**: Rips raw HTML components (buttons, navbars, cards) and their associated CSS styles. Preview them instantly in the interactive Sandbox Modal or download them directly to `.html` files.
  - **3) Audio & Stream Hunter**: Locates `<audio>`, `<source>`, `.mp3`, and `.m3u8` stream links hidden across a site.
  - **4) SEO & Meta Auditor**: Generates a clean audit of Titles, Meta Descriptions, and OpenGraph images.
- **Beautiful HTML Reports**: Output is compiled into an elegant, styled HTML table.

## 📦 Installation

```bash
git clone https://github.com/niktoimiyazap/omnicrawl.git
cd omnicrawl
pip install -r requirements.txt
```

*(Ensure you have Python 3.10+ installed)*

## 🛠️ Usage

Simply run the CLI and follow the interactive prompts:

```bash
python3 main.py
```

### The UI Component Sandbox
When using Mode 2 (UI Component Extractor), the generated `report.html` includes a **Sandbox** button for every discovered element. 
Clicking it opens an isolated `<iframe>` containing the original HTML and all the CSS styles from the source page. You can also click **Download HTML** to get a ready-to-use `.html` file of the stolen component.

## 🧪 Testing

OmniCrawl includes a test suite for its parser logic. Run it via:

```bash
python3 -m unittest discover tests
```

## 📜 License

MIT License. Feel free to use, modify, and distribute.
