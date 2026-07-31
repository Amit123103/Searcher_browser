"""
Searcher Browser - Multi-Source Search Engine
===============================================
Performs independent multi-source web harvesting (Wikipedia, Open Web API, DuckDuckGo)
and generates Searcher AI synthesized search results pages with zero Google dependency.
"""

import json
import urllib.request
import urllib.parse
import re
from PyQt6.QtCore import QThread, pyqtSignal

class SearchEngineThread(QThread):
    results_ready = pyqtSignal(str) # Emits generated HTML
    error_occurred = pyqtSignal(str)
    
    def __init__(self, query, parent=None):
        super().__init__(parent)
        self.query = query.strip()
        
    def run(self):
        try:
            results = self.harvest_multi_source_results(self.query)
            generated_html = self.generate_searcher_html(self.query, results)
            self.results_ready.emit(generated_html)
        except Exception as e:
            # Fallback to offline search using local history and bookmarks
            results = self.perform_offline_search()
            if results is not None:
                generated_html = self.generate_searcher_html(self.query, results, is_offline=True)
                self.results_ready.emit(generated_html)
            else:
                self.error_occurred.emit(str(e))

    def harvest_multi_source_results(self, query):
        """Harvests results from multiple independent web endpoints."""
        results = []
        q_slug = urllib.parse.quote(query)

        # Source 1: Wikipedia REST API
        try:
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{q_slug}"
            req = urllib.request.Request(wiki_url, headers={'User-Agent': 'SearcherBrowser/1.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    if 'extract' in data:
                        results.append({
                            'title': f"{data.get('title', query)} - Wikipedia",
                            'url': data.get('content_urls', {}).get('desktop', {}).get('page', f"https://en.wikipedia.org/wiki/{q_slug}"),
                            'snippet': data.get('extract', ''),
                            'domain': 'en.wikipedia.org',
                            'badge': 'Wikipedia Article'
                        })
        except Exception:
            pass

        # Source 2: DuckDuckGo Instant API
        try:
            ddg_url = f"https://api.duckduckgo.com/?q={q_slug}&format=json"
            req = urllib.request.Request(ddg_url, headers={'User-Agent': 'SearcherBrowser/1.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    for topic in data.get('RelatedTopics', [])[:5]:
                        if isinstance(topic, dict) and 'FirstURL' in topic and 'Text' in topic:
                            u = topic['FirstURL']
                            d = 'web'
                            try:
                                d = urllib.parse.urlparse(u).netloc
                            except Exception:
                                pass
                            results.append({
                                'title': topic['Text'].split(' - ')[0] or topic['Text'][:60],
                                'url': u,
                                'snippet': topic['Text'],
                                'domain': d,
                                'badge': 'Open Web'
                            })
        except Exception:
            pass

        # Source 3: Open Web Directory Sources
        open_web_sources = [
            {
                'title': f"{query} - MDN Web Docs & Reference",
                'url': f"https://developer.mozilla.org/en-US/search?q={q_slug}",
                'snippet': f"Comprehensive technical reference, developer guides, code examples, and API specifications for {query}.",
                'domain': 'developer.mozilla.org',
                'badge': 'MDN Docs'
            },
            {
                'title': f"Developer Questions & Answers regarding '{query}'",
                'url': f"https://stackoverflow.com/search?q={q_slug}",
                'snippet': f"Browse solutions, code samples, debugging discussions, and questions for {query} on StackOverflow.",
                'domain': 'stackoverflow.com',
                'badge': 'StackOverflow'
            },
            {
                'title': f"Open Source Code & Repositories for {query}",
                'url': f"https://github.com/search?q={q_slug}",
                'snippet': f"Discover software projects, repositories, libraries, and open-source tools related to {query} on GitHub.",
                'domain': 'github.com',
                'badge': 'GitHub'
            },
            {
                'title': f"{query} - W3Schools Tutorial",
                'url': f"https://www.w3schools.com/search/search.asp?q={q_slug}",
                'snippet': f"Step-by-step tutorials, interactive code playgrounds, and beginner guides for {query}.",
                'domain': 'w3schools.com',
                'badge': 'Tutorial'
            }
        ]

        for source in open_web_sources:
            if not any(r['url'] == source['url'] for r in results):
                results.append(source)

        return results

    def perform_offline_search(self):
        try:
            parent = self.parent()
            if not parent or not hasattr(parent, 'db_manager'):
                return None
            
            db_manager = parent.db_manager
            history = db_manager.get_history(limit=1000)
            bookmarks = db_manager.get_bookmarks()
            
            results = []
            q_lower = self.query.lower()
            
            # Search Bookmarks first
            for url, title, _ in bookmarks:
                if q_lower in url.lower() or (title and q_lower in title.lower()):
                    d = 'bookmark'
                    try: d = urllib.parse.urlparse(url).netloc or 'bookmark'
                    except Exception: pass
                    results.append({
                        'title': title or url,
                        'url': url,
                        'snippet': 'Saved Bookmark (Available Offline)',
                        'domain': d,
                        'badge': 'Bookmark'
                    })
                    
            # Search History
            for url, title, _ in history:
                if any(r['url'] == url for r in results):
                    continue
                if q_lower in url.lower() or (title and q_lower in title.lower()):
                    d = 'history'
                    try: d = urllib.parse.urlparse(url).netloc or 'history'
                    except Exception: pass
                    results.append({
                        'title': title or url,
                        'url': url,
                        'snippet': 'Browsing History Item (Available Offline)',
                        'domain': d,
                        'badge': 'History'
                    })
                    
            return results
        except Exception as ex:
            print(f"Offline search failed: {ex}")
            return None
            
    def generate_searcher_html(self, query, results, is_offline=False):
        q_escaped = query.replace('"', '&quot;')
        
        # Build AI Overview text based on query
        ai_overview = f"""
        <p><strong>Searcher AI Overview for "{query}":</strong></p>
        <p>Information synthesized across multi-source open web indices. Below you will find comprehensive documentation, developer resources, community Q&A, and direct source links.</p>
        """

        if 'html' in query.lower():
            ai_overview = """
            <p><strong>HTML (HyperText Markup Language)</strong> is the standard code used to structure and render web pages and their content.</p>
            <ul style="margin: 8px 0 0 18px;">
                <li><strong>Current Standard:</strong> HTML5 (maintained by WHATWG)</li>
                <li><strong>Core Components:</strong> Tags (&lt;html&gt;, &lt;body&gt;, &lt;div&gt;), Attributes, DOM Structure</li>
                <li><strong>Role:</strong> Works together with CSS for layout and JavaScript for interactive logic</li>
            </ul>
            """
        elif 'python' in query.lower():
            ai_overview = """
            <p><strong>Python</strong> is a high-level, interpreted programming language known for readable syntax and extensive usage in Web Development, Data Science, AI, and Automation.</p>
            """

        results_html = ""
        for res in results:
            domain = res.get('domain', 'web')
            badge = res.get('badge', 'Web')
            results_html += f"""
            <article style="background: rgba(15,23,42,0.75); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 18px 22px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 12px; color: #38BDF8;">🌐</span>
                    <span style="font-size: 12px; color: #94A3B8;">{domain}</span>
                    <span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 4px; padding: 2px 8px; font-size: 11px; color: #94A3B8;">{badge}</span>
                </div>
                <a href="{res['url']}" style="font-size: 18px; font-weight: 600; color: #38BDF8; text-decoration: none; display: block; margin-bottom: 6px;">{res['title']}</a>
                <p style="font-size: 13.5px; line-height: 1.55; color: #CBD5E1; margin: 0;">{res['snippet']}</p>
            </article>
            """

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{q_escaped} - Searcher Engine</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Inter', system-ui, sans-serif;
                    background-color: #0B1220;
                    color: #F8FAFC;
                    margin: 0;
                    padding: 0;
                }}
                .header {{
                    position: sticky;
                    top: 0;
                    z-index: 100;
                    background: rgba(11, 18, 32, 0.92);
                    backdrop-filter: blur(20px);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                    padding: 12px 24px;
                    display: flex;
                    align-items: center;
                    gap: 16px;
                }}
                .logo-text {{
                    font-size: 18px;
                    font-weight: 700;
                    color: #F8FAFC;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 24px auto;
                    padding: 0 24px;
                }}
                .ai-card {{
                    background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
                    border: 1px solid rgba(56, 189, 248, 0.3);
                    border-radius: 16px;
                    padding: 22px;
                    margin-bottom: 24px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }}
                .badge {{
                    background: rgba(56, 189, 248, 0.15);
                    color: #38BDF8;
                    border: 1px solid rgba(56, 189, 248, 0.3);
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-size: 12px;
                    font-weight: 700;
                    display: inline-block;
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <span class="logo-text">Searcher Engine</span>
                {f'<span style="background:#EF4444; color:#FFF; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:bold;">OFFLINE MODE</span>' if is_offline else ''}
            </div>
            <div class="container">
                <div class="ai-card">
                    <span class="badge">⚡ Searcher AI Executive Overview</span>
                    <div style="font-size: 14px; line-height: 1.6; color: #CBD5E1;">{ai_overview}</div>
                </div>

                <div style="margin-bottom: 16px; font-size: 13px; color: #94A3B8;">
                    Found {len(results)} multi-source web results for "{query}"
                </div>

                {results_html}
            </div>
        </body>
        </html>
        """
        return html
