import html
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from omnicrawl.constants import MODE_CLASSIC, MODE_UI_COMPONENTS, MODE_AUDIO, MODE_SEO, AUDIO_EXTENSIONS
from omnicrawl.utils import is_valid_url, get_base_domain

def extract_internal_links(soup, actual_url, domain_name):
    """Finds all internal links for the crawler queue."""
    links = set()
    for a_tag in soup.find_all("a"):
        href = a_tag.attrs.get("href")
        if not href: continue
        href = urljoin(actual_url, href)
        parsed = urlparse(href)
        href = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        if is_valid_url(href) and domain_name in get_base_domain(href):
            links.add(href)
    return links

def parse_page_data(mode, soup, actual_url, collected_data):
    """Extracts data based on the chosen mode and adds it to collected_data."""
    if mode in (MODE_CLASSIC, MODE_UI_COMPONENTS):
        page_styles = f'<base href="{actual_url}">'
        if mode == MODE_UI_COMPONENTS:
            for tag in soup.find_all(['style', 'link']):
                if tag.name == 'link' and tag.get('rel') != ['stylesheet']:
                    continue
                # Ensure link href is absolute just in case base tag fails
                if tag.name == 'link' and tag.get('href'):
                    tag['href'] = urljoin(actual_url, tag['href'])
                page_styles += str(tag) + "\n"
                
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
                
                if mode == MODE_UI_COMPONENTS:
                    parent = a_tag.parent
                    parent_html = str(parent) if parent else str(a_tag)
                    if len(parent_html) > 1500: 
                        parent_html = str(a_tag)
                    info['html'] = html.escape(parent_html)
                    info['raw_html'] = parent_html
                    info['page_styles'] = page_styles
                    
                collected_data[href] = info
                if mode == MODE_CLASSIC:
                    print(f"\033[92m[+] Discovered Link: {href}\033[0m")
                else:
                    print(f"\033[92m[+] Discovered UI Element: {href}\033[0m")
                    
    elif mode == MODE_AUDIO:
        audio_tags = soup.find_all(["audio", "source", "a"])
        for tag in audio_tags:
            src = tag.attrs.get("src") or tag.attrs.get("href")
            if not src: continue
            
            is_audio = False
            if tag.name == "audio":
                is_audio = True
            elif tag.name == "source" and "audio" in tag.attrs.get("type", ""):
                is_audio = True
            elif src.lower().endswith(AUDIO_EXTENSIONS):
                is_audio = True
                
            if is_audio:
                full_src = urljoin(actual_url, src)
                if full_src not in collected_data:
                    context = tag.parent.get_text(strip=True)[:100] if tag.parent else ""
                    collected_data[full_src] = {'url': full_src, 'type': tag.name, 'context': context}
                    print(f"\033[92m[+] Discovered Audio: {full_src}\033[0m")
                    
    elif mode == MODE_SEO:
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
