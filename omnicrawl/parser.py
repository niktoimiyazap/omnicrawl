import html
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from omnicrawl.constants import MODE_CLASSIC, MODE_UI_COMPONENTS, MODE_AUDIO, MODE_SEO, AUDIO_EXTENSIONS
from omnicrawl.utils import is_valid_url, get_base_domain

def extract_internal_links(soup, actual_url, domain_name, stay_in_domain=True):
    """Finds all internal links for the crawler queue."""
    links = set()
    for a_tag in soup.find_all("a"):
        href = a_tag.attrs.get("href")
        if not href: continue
        href = urljoin(actual_url, href)
        parsed = urlparse(href)
        href = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        if is_valid_url(href):
            if stay_in_domain and domain_name not in get_base_domain(href):
                continue
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
            
            # Determine uniqueness key based on mode
            if mode == MODE_UI_COMPONENTS:
                parent = a_tag.parent
                parent_html = str(parent) if parent else str(a_tag)
                if len(parent_html) > 1500: 
                    parent_html = str(a_tag)
                unique_key = str(hash(parent_html))
            else:
                unique_key = href
                
            if unique_key not in collected_data:
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
                    info['html'] = html.escape(parent_html)
                    info['raw_html'] = parent_html
                    info['page_styles'] = page_styles
                    
                collected_data[unique_key] = info
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
            
            media_assets = []
            og_image_tag = soup.find("meta", attrs={"property": "og:image"})
            if og_image_tag and og_image_tag.attrs.get("content"):
                media_assets.append(urljoin(actual_url, og_image_tag.attrs.get("content").strip()))
                
            for img in soup.find_all("img"):
                src = img.attrs.get("src") or img.attrs.get("data-src")
                if src:
                    full_src = urljoin(actual_url, src.strip())
                    if full_src not in media_assets:
                        media_assets.append(full_src)
                        
            for video in soup.find_all("video"):
                src = video.attrs.get("src")
                if src:
                    full_src = urljoin(actual_url, src.strip())
                    if full_src not in media_assets:
                        media_assets.append(full_src)
                for source in video.find_all("source"):
                    src = source.attrs.get("src")
                    if src:
                        full_src = urljoin(actual_url, src.strip())
                        if full_src not in media_assets:
                            media_assets.append(full_src)
            
            collected_data[actual_url] = {
                'url': actual_url,
                'title': title,
                'description': desc,
                'media': media_assets
            }
            print(f"\033[92m[+] Audited Page: {actual_url}\033[0m")
