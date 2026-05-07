import datetime
from playwright.async_api import async_playwright
from axe_playwright_python.async_playwright import Axe
from backend.schemas import AccessibilityResponse, AxeResultItem, AxeNode
import sys
import asyncio

class AxeService:
    @staticmethod
    async def run_axe(url: str = None, html: str = None, standard: str = "wcag2aa") -> AccessibilityResponse:
        # Extra safety for Windows
        if sys.platform == 'win32' and not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent="MediaWikiAccessibilityChecker/1.0 (https://accessibility-checker.toolforge.org/)"
            )
            page = await context.new_page()

            if url:
                # Normalize URL: prepend https:// if protocol is missing
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                await page.goto(url, wait_until="networkidle")
            elif html:
                await page.set_content(html, wait_until="networkidle")
            else:
                await browser.close()
                raise ValueError("Either URL or HTML must be provided")

            # Run Axe
            axe = Axe()
            # Map standard to axe tags
            # If a specific level is chosen, we include all relevant tags for that level
            guideline = standard or 'wcag2aa'
            
            # Default tags for general WCAG 2.1 AA if not specified
            tags = [guideline]
            if guideline == 'wcag2aa':
                tags = ["wcag2a", "wcag2aa"]
            elif guideline == 'wcag21aa':
                tags = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]
            elif guideline == 'wcag22aa':
                tags = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]
            elif guideline == 'wcag2aaa':
                tags = ["wcag2a", "wcag2aa", "wcag2aaa"]

            results = await axe.run(page, context={
                "include": [["html"]]
            }, options={
                "runOnly": {
                    "type": "tag",
                    "values": tags
                }
            })

            # results = await axe.run(...)

            # Process results into our Schema
            def format_items(items):
                if not items:
                    return []
                formatted = []
                for item in items:
                    # Handle both dict and object access
                    if isinstance(item, dict):
                        id_val = item.get('id', 'unknown')
                        impact_val = item.get('impact')
                        tags_val = item.get('tags', [])
                        desc_val = item.get('description', '')
                        help_val = item.get('help', '')
                        help_url_val = item.get('helpUrl', '')
                        nodes_raw = item.get('nodes', [])
                    else:
                        id_val = getattr(item, 'id', 'unknown')
                        impact_val = getattr(item, 'impact', None)
                        tags_val = getattr(item, 'tags', [])
                        desc_val = getattr(item, 'description', '')
                        help_val = getattr(item, 'help', '')
                        help_url_val = getattr(item, 'help_url', getattr(item, 'helpUrl', ''))
                        nodes_raw = getattr(item, 'nodes', [])

                    nodes = []
                    for node in nodes_raw:
                        if isinstance(node, dict):
                            nodes.append(AxeNode(
                                html=node.get('html', ''),
                                target=node.get('target', []),
                                failureSummary=node.get('failureSummary'),
                                impact=node.get('impact')
                            ))
                        else:
                            nodes.append(AxeNode(
                                html=getattr(node, 'html', ''),
                                target=getattr(node, 'target', []),
                                failureSummary=getattr(node, 'failure_summary', getattr(node, 'failureSummary', None)),
                                impact=getattr(node, 'impact', None)
                            ))
                    
                    formatted.append(AxeResultItem(
                        id=id_val,
                        impact=impact_val,
                        tags=tags_val,
                        description=desc_val,
                        help=help_val,
                        helpUrl=help_url_val,
                        nodes=nodes
                    ))
                return formatted

            # Extract lists from the results.response dictionary
            data = getattr(results, 'response', {})
            
            violations = format_items(data.get('violations', []))
            passes = format_items(data.get('passes', []))
            incomplete = format_items(data.get('incomplete', []))
            inapplicable = format_items(data.get('inapplicable', []))

            response = AccessibilityResponse(
                url=url or "Raw HTML",
                timestamp=datetime.datetime.utcnow().isoformat(),
                violations=violations,
                passes=passes,
                incomplete=incomplete,
                inapplicable=inapplicable,
                summary={
                    "violations": len(violations),
                    "passes": len(passes),
                    "incomplete": len(incomplete),
                    "inapplicable": len(inapplicable)
                }
            )

            # Extra Step: If it's a URL audit, try to fetch full HTML from DOM (Axe truncates by default)
            if url:
                for item_list_name, item_list in [("violations", response.violations), ("incomplete", response.incomplete)]:
                    for item in item_list:
                        for node in item.nodes:
                            try:
                                # Try to find by target selector
                                selectors = node.target
                                if isinstance(selectors, str): selectors = [selectors]
                                selector_to_try = " ".join(selectors)
                                
                                element_data = await page.evaluate("""
                                    (args) => {
                                        const sel = args[0];
                                        const snippet = args[1];
                                        try {
                                            // Strategy A: Direct selector
                                            let el = document.querySelector(sel);
                                            
                                            // Strategy B: If selector fails, try to find by a unique part of the snippet
                                            if (!el && snippet && snippet.length > 20) {
                                                const cleanSnippet = snippet.replace(/\\.\\.\\./g, '').trim();
                                                const all = document.querySelectorAll(sel.split(' ').pop());
                                                for (let candidate of all) {
                                                    if (candidate.outerHTML.includes(cleanSnippet.substring(0, 30))) {
                                                        el = candidate;
                                                        break;
                                                    }
                                                }
                                            }

                                            if (!el) return null;
                                            return { html: el.outerHTML };
                                        } catch (e) { return null; }
                                    }
                                """, [selector_to_try, node.html])
                                
                                if (element_data and element_data['html']):
                                    node.html = element_data['html']
                            except: 
                                continue

            await browser.close()
            return response
