import os
import sys
import webbrowser
import json
from omnicrawl.constants import MODE_CLASSIC, MODE_UI_COMPONENTS, MODE_AUDIO, MODE_SEO

def generate_html_report(domain_name, collected_data, mode):
    report_path = os.path.abspath("report.html")
    
    # Mode-specific table headers and scripts
    extra_head = ""
    extra_body = ""
    if mode == MODE_CLASSIC:
        mode_name = "Classic Links Mapper"
        headers = ["URL", "Link Text", "Tooltip"]
    elif mode == MODE_UI_COMPONENTS:
        mode_name = "UI Component Extractor"
        headers = ["URL", "Link Text", "Actions"]
        # Add Sandbox logic and Download logic
        extra_head = """
    <style>
        /* Sandbox Modal Styles */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4); backdrop-filter: blur(4px); }
        .modal-content { background-color: #ffffff; margin: 5% auto; padding: 24px; border: 1px solid #e2e8f0; width: 85%; max-width: 1200px; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04); }
        .close { color: #94a3b8; float: right; font-size: 24px; font-weight: bold; cursor: pointer; transition: color 0.2s; line-height: 1; }
        .close:hover, .close:focus { color: #0f172a; text-decoration: none; cursor: pointer; }
        
        .action-group { display: flex; gap: 8px; }
        .sandbox-btn { background: transparent; color: #3b82f6; border: 1px solid #bfdbfe; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 13px; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; }
        .sandbox-btn:hover { background: #eff6ff; border-color: #93c5fd; }
        .sandbox-btn svg { width: 14px; height: 14px; fill: currentColor; }
        
        .download-btn { background: transparent; color: #10b981; border: 1px solid #a7f3d0; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 13px; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; }
        .download-btn:hover { background: #ecfdf5; border-color: #6ee7b7; }
        .download-btn svg { width: 14px; height: 14px; fill: currentColor; }
        
        #sandbox-iframe { width: 100%; min-height: 400px; border: 1px dashed #cbd5e1; border-radius: 6px; background: #fff; margin-top: 16px; }
    </style>
        """
        extra_body = """
    <!-- The Modal -->
    <div id="sandboxModal" class="modal">
      <div class="modal-content">
        <span class="close">&times;</span>
        <h2 style="margin-top:0; color: #0f172a;">UI Sandbox Preview</h2>
        <p style="color: #64748b; font-size: 14px; margin-top: -10px;">The component is rendered in an isolated iframe with its original CSS styles attached.</p>
        <iframe id="sandbox-iframe" src="about:blank"></iframe>
      </div>
    </div>
    
    <script>
        var modal = document.getElementById("sandboxModal");
        var span = document.getElementsByClassName("close")[0];
        var iframe = document.getElementById("sandbox-iframe");
        
        function openSandbox(rawHtml, pageStyles) {
            var doc = iframe.contentWindow.document;
            doc.open();
            doc.write('<!DOCTYPE html><html><head>' + (pageStyles || '') + '</head><body style="padding: 20px; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh;">' + rawHtml + '</body></html>');
            doc.close();
            modal.style.display = "block";
        }
        
        function downloadComponent(rawHtml, pageStyles, filename) {
            var content = '<!DOCTYPE html><html><head>' + (pageStyles || '') + '</head><body style="padding: 20px; margin: 0;">' + rawHtml + '</body></html>';
            var blob = new Blob([content], { type: 'text/html' });
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        }
        
        span.onclick = function() {
            modal.style.display = "none";
            iframe.src = "about:blank";
        }
        
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
                iframe.src = "about:blank";
            }
        }
    </script>
        """
    elif mode == MODE_AUDIO:
        mode_name = "Audio & Stream Hunter"
        headers = ["Media URL", "Element Type", "Context / Text"]
    elif mode == MODE_SEO:
        mode_name = "SEO & Meta Auditor"
        headers = ["Page URL", "Title & Description", "OG Image"]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniCrawl Report - {domain_name}</title>
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
        
        /* Media & SEO Styles */
        .og-wrapper {{ display: flex; flex-direction: column; gap: 8px; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; padding: 8px; border-radius: 8px; flex-shrink: 0; content-visibility: auto; contain-intrinsic-size: 150px; }}
        .og-preview {{ max-width: 120px; max-height: 120px; object-fit: contain; border-radius: 4px; }}
        .download-img-btn {{ background: #fff; color: #4f46e5; border: 1px solid #c7d2fe; padding: 6px; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 12px; display: inline-flex; align-items: center; gap: 4px; transition: all 0.2s; text-decoration: none !important; width: 100%; justify-content: center; box-sizing: border-box; }}
        .download-img-btn:hover {{ background: #e0e7ff; border-color: #a5b4fc; text-decoration: none !important; }}
        .download-img-btn svg {{ width: 14px; height: 14px; fill: currentColor; }}
    </style>{extra_head}
</head>
<body>
    <h1>OmniCrawl Report: {domain_name}</h1>
    <h2>Mode: {mode_name} | Total Items: {len(collected_data)}</h2>
    <table style="table-layout: fixed; width: 100%;">
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
        html_content += '            <tr style="content-visibility: auto; contain-intrinsic-size: 100px;">\n'
        if mode == MODE_CLASSIC:
            html_content += f"""                <td style="word-break: break-word;"><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td style="word-break: break-word;">{info['text']}</td>
                <td style="word-break: break-word;">{info['tooltip']}</td>\n"""
        elif mode == MODE_UI_COMPONENTS:
            import html
            raw_html_js = html.escape(json.dumps(info['raw_html']))
            page_styles_js = html.escape(json.dumps(info.get('page_styles', '')))
            play_icon = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>'
            dl_icon = '<svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>'
            filename = f"component_{abs(hash(info['url']))}.html"
            
            html_content += f"""                <td style="word-break: break-word;"><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td style="word-break: break-word;">{info['text']}</td>
                <td>
                    <div class="action-group">
                        <button class="sandbox-btn" onclick="openSandbox({raw_html_js}, {page_styles_js})">{play_icon} Sandbox</button>
                        <button class="download-btn" onclick="downloadComponent({raw_html_js}, {page_styles_js}, '{filename}')">{dl_icon} Download HTML</button>
                    </div>
                </td>\n"""
        elif mode == MODE_AUDIO:
            html_content += f"""                <td style="word-break: break-word;"><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td><span style="background: #e5e7eb; padding: 2px 6px; border-radius: 4px; white-space: nowrap;">{info['type']}</span></td>
                <td style="word-break: break-word;">{info['context']}</td>\n"""
        elif mode == MODE_SEO:
            dl_icon = '<svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>'
            media_html = ""
            if info.get("media"):
                media_html = '<div style="display: flex; gap: 8px; flex-wrap: wrap; max-height: 200px; overflow-y: auto; padding: 4px;">'
                for m_url in info["media"]:
                    # simple heuristic for video vs image
                    if m_url.lower().endswith(('.mp4', '.webm', '.ogg', '.m3u8')):
                        preview = f'<video src="{m_url}" class="og-preview" preload="none" muted loop onmouseover="this.play()" onmouseout="this.pause()"></video>'
                    else:
                        preview = f'<img src="{m_url}" class="og-preview" loading="lazy" decoding="async">'
                    media_html += f"""
                    <div class="og-wrapper">
                        {preview}
                        <a href="{m_url}" target="_blank" download class="download-img-btn">{dl_icon} Download</a>
                    </div>"""
                media_html += '</div>'
            else:
                media_html = "<span style='color: #94a3b8; font-size: 12px;'>No Media</span>"
                
            html_content += f"""                <td style="word-break: break-all;"><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td style="word-break: break-word;">
                    <div style="font-weight: 600; color: #1e293b; margin-bottom: 4px; font-size: 14px;">{info['title'] or 'No Title'}</div>
                    <div style="color: #475569; font-size: 13px; line-height: 1.4;">{info['description'] or 'No Description'}</div>
                </td>
                <td>{media_html}</td>\n"""
        html_content += "            </tr>\n"

    html_content += f"""        </tbody>
    </table>
{extra_body}
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
