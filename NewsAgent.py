# NewsAgent.py

from NewsTasks import categorize_article, summarize_article
from NewsTools import call_openrouter_model

# Agent logic (LiteLLM-based, can be modified)
def news_agent(prompt: str):
    return call_openrouter_model(prompt)

# Categorizer agent
def categorizer_agent(prompt: str):
    return news_agent(prompt)

# Summarizer agent
def summarizer_agent(prompt: str):
    return news_agent(prompt)

# Create categorize task wrapper
def get_categorize_task():
    return lambda title, content: categorize_article(title, content)

# Create summarize task wrapper
def get_summarize_task():
    return lambda title, content: summarize_article(title, content)

# Unified article processor
def process_article(title, content, link):
    category = get_categorize_task()(title, content)
    summary = get_summarize_task()(title, content)
    return {
        "title": title,
        "content": content,
        "summary": summary,
        "category": category,
        "link": link
    }