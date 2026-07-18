import urllib.request
import urllib.parse
from html.parser import HTMLParser
from PyQt6.QtCore import QThread, pyqtSignal

class DDGLiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.in_result_title = False
        self.in_result_snippet = False
        self.current_url = ""
        self.current_title = ""
        self.current_snippet = ""
        self.capture_snippet = False
        
    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        
        # Detect the title link
        if tag == 'a' and attr_dict.get('class') == 'result-link':
            self.current_url = attr_dict.get('href', '')
            self.in_result_title = True
            
        # Detect snippet (class 'result-snippet')
        if tag == 'td' and attr_dict.get('class') == 'result-snippet':
            self.in_result_snippet = True
            
    def handle_endtag(self, tag):
        if tag == 'a' and self.in_result_title:
            self.in_result_title = False
        if tag == 'td' and self.in_result_snippet:
            self.in_result_snippet = False
            # We finished one full result block (hopefully)
            if self.current_url and self.current_title:
                url = self.current_url.strip()
                if url.startswith('/l/?uddg='):
                    import urllib.parse
                    url = urllib.parse.unquote(url.split('uddg=')[1].split('&')[0])
                elif url.startswith('//'):
                    url = 'https:' + url
                    
                self.results.append({
                    'title': self.current_title.strip(),
                    'url': url,
                    'snippet': self.current_snippet.strip()
                })
                self.current_url = ""
                self.current_title = ""
                self.current_snippet = ""
                
    def handle_data(self, data):
        if self.in_result_title:
            self.current_title += data
        if self.in_result_snippet:
            self.current_snippet += data

class SearchEngineThread(QThread):
    results_ready = pyqtSignal(str) # Emits the generated HTML
    error_occurred = pyqtSignal(str)
    
    def __init__(self, query, parent=None):
        super().__init__(parent)
        self.query = query
        
    def run(self):
        try:
            url = "https://lite.duckduckgo.com/lite/"
            data = urllib.parse.urlencode({'q': self.query}).encode('utf-8')
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode('utf-8')
                
            parser = DDGLiteParser()
            parser.feed(html)
            
            generated_html = self.generate_searcher_html(self.query, parser.results)
            self.results_ready.emit(generated_html)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            
    def generate_searcher_html(self, query, results):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{query} - Searcher</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #222222;
                    color: #e8eaed;
                    margin: 0;
                    padding: 0;
                }}
                .header {{
                    padding: 20px 40px;
                    display: flex;
                    align-items: center;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #a78bfa;
                    margin-right: 30px;
                }}
                .search-bar {{
                    background: #2a2a2a;
                    border: 1px solid #444;
                    border-radius: 15px;
                    padding: 8px 16px;
                    color: #fff;
                    width: 500px;
                    font-size: 14px;
                }}
                .container {{
                    max-width: 700px;
                    margin: 20px 40px;
                }}
                .result {{
                    margin-bottom: 25px;
                }}
                .result-title {{
                    font-size: 18px;
                    color: #60a5fa;
                    text-decoration: none;
                }}
                .result-title:hover {{
                    text-decoration: underline;
                }}
                .result-url {{
                    color: #9ca3af;
                    font-size: 13px;
                    margin-bottom: 5px;
                }}
                .result-snippet {{
                    color: #9ca3af;
                    font-size: 14px;
                    line-height: 1.5;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">Searcher</div>
                <div class="search-bar">{query}</div>
            </div>
            <div class="container">
        """
        
        if not results:
            html += "<p>No results found. (Or DDG blocked the request).</p>"
            
        for res in results:
            html += f"""
                <div class="result">
                    <div class="result-url">{res['url']}</div>
                    <a href="{res['url']}" class="result-title">{res['title']}</a>
                    <div class="result-snippet">{res['snippet']}</div>
                </div>
            """
            
        html += """
            </div>
        </body>
        </html>
        """
        return html
