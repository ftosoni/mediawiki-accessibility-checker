import json
import csv
import io
import datetime
import base64
import pytz
import re
import html
from typing import List
from playwright.async_api import async_playwright
from backend.schemas import AccessibilityResponse

class ExportService:
    @staticmethod
    def to_json(results: AccessibilityResponse) -> str:
        return results.model_dump_json(indent=2)

    @staticmethod
    def to_csv(results: AccessibilityResponse) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Type", "ID", "Impact", "Help", "Description", "URL", "Selector", "HTML", "Fix"])
        
        for item_list, type_name in [(results.violations, "Violation"), 
                                   (results.incomplete, "Incomplete"), 
                                   (results.passes, "Pass")]:
            for item in item_list:
                for node in item.nodes:
                    writer.writerow([
                        type_name,
                        item.id,
                        item.impact or "",
                        item.help,
                        item.description,
                        item.helpUrl,
                        " ".join(node.target) if isinstance(node.target, list) else node.target,
                        node.html,
                        node.failureSummary or ""
                    ])
        return output.getvalue()

    @staticmethod
    def to_wikitext(results: AccessibilityResponse) -> str:
        lines = []
        lines.append(f"== Accessibility Report for {results.title or results.url} ==")
        lines.append(f"URL: {results.url}")
        lines.append(f"Generated on: {results.timestamp}")
        lines.append("")
        
        for item_list, title in [(results.violations, "Violations"), 
                                (results.incomplete, "Incomplete"), 
                                (results.passes, "Passes")]:
            if not item_list:
                continue
                
            lines.append(f"=== {title} ({len(item_list)}) ===")
            lines.append('{| class="wikitable" style="width: 100%;"')
            lines.append('! Impact !! Rule !! Description !! Elements')
            
            for item in item_list:
                nodes_desc = []
                for node in item.nodes:
                    sel = " ".join(node.target) if isinstance(node.target, list) else node.target
                    nodes_desc.append(f"* Selector: <code>{sel}</code>")
                
                nodes_str = "\n".join(nodes_desc)
                lines.append("|-")
                lines.append(f"| {item.impact or 'N/A'} || [[{item.helpUrl}|{item.help}]] || {item.description} || {nodes_str}")
                
            lines.append("|}")
            lines.append("")
            
        return "\n".join(lines)

    @staticmethod
    def get_formatted_timestamps_html(iso_ts: str) -> str:
        dt = datetime.datetime.fromisoformat(iso_ts.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        
        formats = [
            ("GMT", pytz.utc),
            ("CEST", pytz.timezone("Europe/Rome")),
            ("IST", pytz.timezone("Asia/Kolkata")),
            ("PT", pytz.timezone("America/Los_Angeles"))
        ]
        
        html_rows = []
        for name, tz in formats:
            localized = dt.astimezone(tz)
            html_rows.append(f'<tr><td style="padding: 0 8px 0 0; font-weight: bold; text-align: right;">{name}:</td><td style="text-align: right;">{localized.strftime("%Y-%m-%d %H:%M:%S")}</td></tr>')
        
        return f'<table style="font-size: 10px; border-collapse: collapse; margin-left: auto;">{"".join(html_rows)}</table>'

    @staticmethod
    async def to_pdf(results: AccessibilityResponse, logo_path: str = None) -> bytes:
        logo_base64 = ""
        if logo_path:
            try:
                with open(logo_path, "rb") as image_file:
                    logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            except:
                pass

        formatted_ts_html = ExportService.get_formatted_timestamps_html(results.timestamp)

        def resolve_img_preview(node_html, base_url):
            img_match = re.search(r'<img[^>]+>', node_html, re.I)
            if not img_match:
                return ""
            
            img_tag = img_match.group(0)
            src_match = re.search(r'(?:src|data-src|srcset)=["\'](.*?)["\']', img_tag, re.I)
            if not src_match:
                return ""
            
            src = src_match.group(1).split(',')[0].split(' ')[0].strip()
            if not src:
                return ""

            resolved_src = src
            if src.startswith('//'):
                resolved_src = 'https:' + src
            elif src.startswith('/') and base_url:
                from urllib.parse import urljoin
                resolved_src = urljoin(base_url, src)
            elif not src.startswith('http') and base_url:
                from urllib.parse import urljoin
                resolved_src = urljoin(base_url, src)
            
            return f"""
                <div class="node-preview" style="margin-bottom: 8px;">
                    <img src="{resolved_src}" 
                         style="max-width: 160px; max-height: 120px; border: 1px solid #eaecf0; border-radius: 2px; background: #fff;" />
                </div>
            """

        def build_issue_html(item, base_url):
            nodes_html = ""
            for node in item.nodes:
                target_str = " ".join(node.target) if isinstance(node.target, list) else node.target
                img_preview = resolve_img_preview(node.html, base_url)
                safe_fix = html.escape(node.failureSummary or "N/A")
                
                nodes_html += f"""
                    <div class="node-item">
                        <span class="node-selector">{html.escape(target_str)}</span>
                        {img_preview}
                        <div class="node-fix"><strong>Fix:</strong> {safe_fix}</div>
                    </div>
                """
            
            return f"""
                <div class="issue">
                    <div class="issue-header">
                        <h3 class="issue-title">{html.escape(item.help)}</h3>
                        <span class="impact-label impact-{item.impact or 'minor'}">{item.impact or 'N/A'}</span>
                    </div>
                    <div class="issue-body">
                        <div class="issue-desc">{html.escape(item.description)}</div>
                        {nodes_html}
                    </div>
                </div>
            """

        violations_html = "".join([build_issue_html(item, results.url) for item in results.violations])
        incomplete_html = "".join([build_issue_html(item, results.url) for item in results.incomplete])

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Inter', 'Roboto', sans-serif; color: #202122; margin: 25px; line-height: 1.4; font-size: 11.5px; }}
                
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding-bottom: 15px; border-bottom: 2px solid #36c; }}
                
                .logo-container {{ flex-shrink: 0; text-align: left; }}
                .logo {{ max-width: 200px; max-height: 100px; display: block; margin-bottom: 4px; }}
                .logo-credit {{ font-size: 8px; color: #72777d; line-height: 1.1; }}
                
                .header-info {{ text-align: right; flex: 1; margin-left: 30px; }}
                .header-info h1 {{ margin: 0 0 2px 0; color: #36c; font-size: 19px; font-weight: 700; }}
                .header-info .tool-url {{ font-size: 11px; color: #36c; margin-bottom: 8px; display: block; font-weight: 600; text-decoration: none; }}
                
                .header-meta {{ font-size: 10px; color: #54595d; }}
                .header-meta p {{ margin: 3px 0; }}
                .audit-times-label {{ font-weight: bold; margin-top: 8px; display: block; }}
                
                .summary {{ display: flex; gap: 10px; margin: 20px 0; }}
                .summary-card {{ flex: 1; padding: 10px; border-radius: 4px; text-align: center; color: white; }}
                .violations {{ background: #d73333; }}
                .incomplete {{ background: #ac6600; }}
                .passes {{ background: #14866d; }}
                .summary-card h2 {{ margin: 0; font-size: 20px; }}
                .summary-card p {{ margin: 0; font-size: 9px; font-weight: bold; text-transform: uppercase; }}
                
                .section-title {{ border-bottom: 1px solid #eaecf0; padding-bottom: 5px; margin: 25px 0 12px 0; color: #202122; font-size: 15px; font-weight: bold; }}
                
                .issue {{ margin-bottom: 15px; border: 1px solid #eaecf0; border-radius: 4px; overflow: visible; }}
                .issue-header {{ padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; background: #f8f9fa; border-bottom: 1px solid #eaecf0; page-break-inside: avoid; }}
                .issue-title {{ font-weight: bold; font-size: 13px; margin: 0; flex: 1; }}
                .impact-label {{ padding: 2px 6px; border-radius: 2px; font-size: 9px; font-weight: bold; text-transform: uppercase; margin-left: 10px; flex-shrink: 0; }}
                .impact-critical {{ background: #000; color: #fff; }}
                .impact-serious {{ background: #d73333; color: #fff; }}
                .impact-moderate {{ background: #ac6600; color: #fff; }}
                .impact-minor {{ background: #72777d; color: #fff; }}
                
                .issue-body {{ padding: 10px 12px; overflow: visible; }}
                .issue-desc {{ margin-bottom: 8px; color: #202122; font-weight: 500; }}
                .node-item {{ background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 8px; border-left: 4px solid #36c; overflow-wrap: break-word; }}
                .node-selector {{ font-family: monospace; font-size: 10px; color: #36c; display: block; margin-bottom: 5px; }}
                .node-fix {{ font-size: 10.5px; color: #54595d; white-space: pre-wrap; line-height: 1.5; }}
                
                .footer {{ margin-top: 40px; padding-top: 15px; border-top: 1px solid #eaecf0; font-size: 9px; color: #72777d; text-align: center; }}
                .footer a {{ color: #36c; text-decoration: none; font-weight: 500; }}
                .footer-credits {{ margin-top: 5px; font-size: 8.5px; }}
                
                @media print {{
                    .issue {{ break-inside: auto; }}
                    .node-item {{ break-inside: avoid; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo-container">
                    {f'<img src="data:image/jpeg;base64,{logo_base64}" class="logo" />' if logo_base64 else ''}
                    <div class="logo-credit">Logo by Kuldeepburjbhalaike | CC BY-SA 4.0</div>
                </div>
                <div class="header-info">
                    <h1>MediaWiki Accessibility Checker</h1>
                    <a class="tool-url" href="https://accessibility-checker.toolforge.org/">accessibility-checker.toolforge.org</a>
                    
                    <div class="header-meta">
                        <p><strong>Page Title:</strong> {html.escape(results.title or "N/A")}</p>
                        <p><strong>Audited URL:</strong> {html.escape(results.url)}</p>
                        <div style="margin-top: 8px;">
                            <span class="audit-times-label">Audit Timestamps</span>
                            {formatted_ts_html}
                        </div>
                    </div>
                </div>
            </div>

            <div class="summary">
                <div class="summary-card violations">
                    <h2>{results.summary.get('violations', 0)}</h2>
                    <p>Violations</p>
                </div>
                <div class="summary-card incomplete">
                    <h2>{results.summary.get('incomplete', 0)}</h2>
                    <p>Incomplete</p>
                </div>
                <div class="summary-card passes">
                    <h2>{results.summary.get('passes', 0)}</h2>
                    <p>Passes</p>
                </div>
            </div>

            <h2 class="section-title">Violations</h2>
            {violations_html if violations_html else "<p>No violations found.</p>"}

            {f'<h2 class="section-title">Incomplete Checks</h2>{incomplete_html}' if incomplete_html else ''}

            <div class="footer">
                <div>
                    Report generated by <a href="https://accessibility-checker.toolforge.org/">MediaWiki Accessibility Checker</a> | 
                    Powered by <a href="https://github.com/dequelabs/axe-core">axe-core</a>
                </div>
                <div class="footer-credits">
                    Developed by <a href="https://meta.wikimedia.org/wiki/Special:MyLanguage/User:Super_nabla">Francesco Tosoni (Super nabla)</a> | 
                    License: <a href="https://github.com/ftosoni/mediawiki-accessibility-checker/blob/main/LICENSE">MPL-2.0</a>
                </div>
            </div>
        </body>
        </html>
        """

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_content(html_content)
            await page.wait_for_timeout(500) 
            pdf_bytes = await page.pdf(
                format="A4", 
                print_background=True,
                margin={ "top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm" }
            )
            await browser.close()
            return pdf_bytes
