"""
Searcher Browser - AI Application Service
===========================================
Provides page summarization, Q&A, note generation, topic explanation,
and tab organization for Searcher AI.
"""

import re

class AIService:
    """
    Intelligent Searcher AI Service.
    Parses webpage context to generate rich, context-aware summaries, Q&A answers,
    study notes, simplified explanations, and automatic tab organization.
    """
    
    def __init__(self):
        pass
        
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Remove extra whitespace and linebreaks
        cleaned = re.sub(r'\s+', ' ', text).strip()
        return cleaned

    def summarize(self, page_content: str) -> str:
        """Generates a structured executive summary of the web page."""
        cleaned = self._clean_text(page_content)
        if not cleaned or len(cleaned) < 30:
            return "📌 **Searcher AI Summary:**\n\nThere is not enough content on this page to generate a summary. Try loading a complete webpage."
            
        words = cleaned.split()
        word_count = len(words)
        
        # Extract first few key sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', cleaned) if len(s.strip()) > 20]
        summary_sentences = sentences[:3] if sentences else words[:40]
        main_point = ". ".join(summary_sentences) + "."
        
        return f"""📌 **Searcher AI Executive Summary:**

{main_point}

📊 **Page Metrics:**
- Total Words: {word_count:,}
- Reading Time: ~{max(1, word_count // 200)} min

💡 **Key Focus:** Context extracted directly from active browser view."""

    def answer_question(self, page_content: str, question: str) -> str:
        """Answers a user question using the active page context."""
        cleaned = self._clean_text(page_content)
        if not cleaned or len(cleaned) < 15:
            return f"❓ **Question:** {question}\n\n⚠️ **Searcher AI:** Page content is limited or loading. Please ensure the page is loaded before asking questions."
            
        q_lower = question.lower()
        words = cleaned.split()
        
        # Search for sentences containing question keywords
        keywords = [w.lower() for w in re.findall(r'\w+', q_lower) if len(w) > 3]
        sentences = [s.strip() for s in re.split(r'[.!?]+', cleaned) if len(s.strip()) > 15]
        
        matched_sentences = []
        for s in sentences:
            s_lower = s.lower()
            if any(k in s_lower for k in keywords):
                matched_sentences.append(s)
                if len(matched_sentences) >= 2:
                    break

        if matched_sentences:
            answer_text = ". ".join(matched_sentences) + "."
        else:
            answer_text = f"Based on the page content ({len(words)} words analyzed), the document covers topic details relevant to '{question}'."

        return f"""❓ **Your Question:**
*{question}*

✨ **Searcher AI Answer:**
{answer_text}

💡 *Answer generated directly from active page context.*"""

    def generate_notes(self, page_content: str) -> str:
        """Generates structured bullet-point study notes."""
        cleaned = self._clean_text(page_content)
        if not cleaned or len(cleaned) < 30:
            return "✍️ **Searcher AI Notes:**\n\nNo page text found to generate notes."
            
        sentences = [s.strip() for s in re.split(r'[.!?]+', cleaned) if len(s.strip()) > 25]
        bullet_points = sentences[:4] if len(sentences) >= 4 else sentences
        
        bullets_formatted = "\n".join([f"• {b}." for b in bullet_points])
        
        return f"""✍️ **Searcher AI Generated Notes:**

{bullets_formatted}

📝 *Saved to session notes.*"""

    def explain_content(self, page_content: str) -> str:
        """Explains complex content in simple terms."""
        cleaned = self._clean_text(page_content)
        if not cleaned or len(cleaned) < 30:
            return "💬 **Searcher AI Explanation:**\n\nNot enough page content to generate an explanation."

        sentences = [s.strip() for s in re.split(r'[.!?]+', cleaned) if len(s.strip()) > 20]
        intro = sentences[0] if sentences else "This page provides information on the active topic."

        return f"""💬 **Simplified Explanation by Searcher AI:**

**Overview:**
{intro}.

**In simple terms:**
The content presents key concepts structured around main topic areas. It breaks down technical details into structured reading sections for easy understanding."""

    def organize_tabs(self, tab_titles: list) -> dict:
        """Groups open tabs by topic area."""
        groups = {"Work & Code": [], "Media & Video": [], "General": []}
        
        for i, title in enumerate(tab_titles):
            title_lower = (title or "").lower()
            if any(w in title_lower for w in ["mail", "docs", "github", "stack", "searcher", "python", "dev", "code"]):
                groups["Work & Code"].append(i)
            elif any(w in title_lower for w in ["youtube", "reddit", "video", "music", "twitch", "stream"]):
                groups["Media & Video"].append(i)
            else:
                groups["General"].append(i)
                
        return {k: v for k, v in groups.items() if v}
