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
        headers = ["URL", "Link Text", "Component HTML", "Sandbox"]
        # Add highlight.js for syntax highlighting and Sandbox logic
        extra_head = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <script>document.addEventListener('DOMContentLoaded', (event) => { document.querySelectorAll('pre code').forEach((el) => { hljs.highlightElement(el); }); });</script>
    <style>
        /* Sandbox Modal Styles */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4); }
        .modal-content { background-color: #fefefe; margin: 5% auto; padding: 20px; border: 1px solid #888; width: 80%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close:hover, .close:focus { color: black; text-decoration: none; cursor: pointer; }
        .sandbox-btn { background: #10b981; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 14px; display: inline-flex; align-items: center; gap: 6px; }
        .sandbox-btn:hover { background: #059669; }
        #sandbox-container { border: 1px dashed #cbd5e1; padding: 20px; min-height: 100px; margin-top: 15px; border-radius: 4px; background: #fff; }
    </style>
        """
        extra_body = """
    <!-- The Modal -->
    <div id="sandboxModal" class="modal">
      <div class="modal-content">
        <span class="close">&times;</span>
        <h2>UI Sandbox Preview</h2>
        <p style="color: #64748b; font-size: 14px; margin-top: 0;">Below is how the component renders visually in the browser.</p>
        <div id="sandbox-container"></div>
      </div>
    </div>
    
    <script>
        var modal = document.getElementById("sandboxModal");
        var span = document.getElementsByClassName("close")[0];
        var container = document.getElementById("sandbox-container");
        
        function openSandbox(rawHtml) {
            container.innerHTML = rawHtml;
            modal.style.display = "block";
        }
        
        span.onclick = function() {
            modal.style.display = "none";
            container.innerHTML = "";
        }
        
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
                container.innerHTML = "";
            }
        }
    </script>
        """
    elif mode == MODE_AUDIO:
        mode_name = "Audio & Stream Hunter"
        headers = ["Media URL", "Element Type", "Context / Text"]
    elif mode == MODE_SEO:
        mode_name = "SEO & Meta Auditor"
        headers = ["Page URL", "Title", "Meta Description", "OG Image"]

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
        pre {{ margin: 0; max-width: 500px; max-height: 200px; overflow: auto; border-radius: 4px; font-size: 12px; }}
        img.og-preview {{ max-width: 150px; border-radius: 4px; border: 1px solid #e5e7eb; }}
    </style>{extra_head}
</head>
<body>
    <h1>OmniCrawl Report: {domain_name}</h1>
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
        if mode == MODE_CLASSIC:
            html_content += f"""                <td><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td>{info['text']}</td>
                <td>{info['tooltip']}</td>\n"""
        elif mode == MODE_UI_COMPONENTS:
            raw_html_js = json.dumps(info['raw_html'])
            html_content += f"""                <td><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td>{info['text']}</td>
                <td><pre><code class="language-html">{info['html']}</code></pre></td>
                <td><button class="sandbox-btn" onclick='openSandbox({raw_html_js})'>▶️ Sandbox</button></td>\n"""
        elif mode == MODE_AUDIO:
            html_content += f"""                <td><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td><span style="background: #e5e7eb; padding: 2px 6px; border-radius: 4px;">{info['type']}</span></td>
                <td>{info['context']}</td>\n"""
        elif mode == MODE_SEO:
            img_tag = f'<img src="{info["og_image"]}" class="og-preview">' if info["og_image"] else "No Image"
            html_content += f"""                <td><a href="{info['url']}" target="_blank">{info['url']}</a></td>
                <td><strong>{info['title']}</strong></td>
                <td>{info['description']}</td>
                <td>{img_tag}</td>\n"""
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
