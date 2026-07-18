import time

class AIService:
    """
    Mock AI Service for Phase 4.
    Simulates calling an LLM API (like Google Gemini) to avoid requiring API keys for the demo.
    """
    
    def __init__(self):
        pass
        
    def summarize(self, page_content):
        """Simulates summarizing a web page."""
        # time.sleep(0.5)  # Simulate network delay (avoiding real sleep to keep UI responsive without threads)
        if not page_content or len(page_content.strip()) < 20:
            return "There is not enough content on this page to summarize."
            
        word_count = len(page_content.split())
        return f"**Summary:**\nThis page contains roughly {word_count} words. It appears to cover topics relevant to the title and main headers. (This is a simulated AI summary)."
        
    def answer_question(self, page_content, question):
        """Simulates answering a question based on page context."""
        if not page_content or len(page_content.strip()) < 10:
            return f"📝 **Question:** {question}\n\n❌ **Response:** I need more content from the page to provide a meaningful answer. The current page appears to be empty or not fully loaded."
            
        word_count = len(page_content.split())
        char_count = len(page_content)
        
        return f"""📝 **Your Question:**
{question}

✅ **AI Response:**
Based on the {word_count} words ({char_count} characters) of content from this page, I've analyzed the information provided. The page contains relevant information about your query. 

**Key Insight:** This is a simulated intelligent response. In a production environment, a real LLM would extract the most relevant information from the page content to answer your question specifically.

**Tip:** Try asking follow-up questions to explore more details about this page."""
        
    def generate_notes(self, page_content):
        """Simulates generating study notes or bullet points."""
        if not page_content:
            return "No content to generate notes from."
            
        return "**Key Takeaways:**\n- Point 1: The page has interesting text.\n- Point 2: Consider reading the bolded sections.\n- Point 3: This is a simulated generated note structure."
        
    def organize_tabs(self, tab_titles):
        """
        Simulates grouping tabs by topic.
        Returns a dictionary mapping Group Name -> List of tab indices.
        """
        groups = {"Work/Dev": [], "Media": [], "General": []}
        
        for i, title in enumerate(tab_titles):
            title_lower = title.lower()
            if any(w in title_lower for w in ["mail", "docs", "github", "stack", "searcher"]):
                groups["Work/Dev"].append(i)
            elif any(w in title_lower for w in ["youtube", "reddit", "video", "music", "twitch"]):
                groups["Media"].append(i)
            else:
                groups["General"].append(i)
                
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
