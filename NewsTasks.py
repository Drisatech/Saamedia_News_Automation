# NewsTasks.py

def categorize_article(title: str, content: str) -> str:
    """
    Categorize the article based on content.
    This is a placeholder — replace with AI categorization logic.
    """
    if "election" in content.lower():
        return "Politics"
    elif "economy" in content.lower():
        return "Business"
    elif "sport" in content.lower():
        return "Sports"
    else:
        return "General"

def summarize_article(title: str, content: str) -> str:
    """
    Summarize the article content.
    This is a placeholder — replace with AI summarization logic.
    """
    return content[:200] + "..." if len(content) > 200 else content