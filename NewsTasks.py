# NewsTasks.py

from crewai import Task
from NewsAgent import news_agent
from NewsTools import get_current_datetime
from db import insert_article

def get_categorize_task(agent):
    return Task(
        description=(
            "Classify the news article into an appropriate category such as "
            "'Politics', 'Business', 'Entertainment', 'Technology', 'Sports', or 'Health'.\n\n"
            "Article title: {title}\n"
            "Content:\n{content}"
        ),
        expected_output="The appropriate category label for the article.",
        agent=agent,
        output_key="category"
    )

def get_summarize_task(agent):
    return Task(
        description=(
            "Generate a concise and clear summary of the following news article. "
            "Focus on key facts and relevant context.\n\n"
            "Title: {title}\n"
            "Content:\n{content}"
        ),
        expected_output="A well-written summary paragraph (2–3 sentences) of the article.",
        agent=agent,
        output_key="summary"
    )

def scrape_latest_articles():
    """
    Run the news_agent to fetch fresh articles (AI-powered or web scraped),
    then insert into SQLite for persistence.
    """
    print("🚀 Running News Agent to fetch latest articles...")

    result = news_agent.run()
    if not result or not isinstance(result, list):
        print("⚠️ No valid result from News Agent.")
        return []

    inserted = 0
    for article in result:
        title = article.get("title")
        content = article.get("content")
        source = article.get("link") or article.get("source")
        category = article.get("category", "Uncategorized")
        image_url = article.get("image_url")

        success = insert_article(title, content, source, category, image_url)
        if success:
            inserted += 1

    print(f"✅ {inserted} new articles inserted into database.")
    return result