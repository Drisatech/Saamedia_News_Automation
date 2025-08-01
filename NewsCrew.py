# NewsCrew.py

import logging
from NewsTasks import get_categorize_task, get_summarize_task
from NewsAgent import categorizer_agent, summarizer_agent
from NewsAgent import process_article
from NewsTools import scrape_latest_articles  # ensure this exists and returns dicts

logging.basicConfig(
    filename='newscrew.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Prepare agents and tasks as lists
agents = [categorizer_agent, summarizer_agent]
tasks = [
    get_categorize_task(categorizer_agent),
    get_summarize_task(summarizer_agent)
]

def run_news_pipeline():
    try:
        logging.info("Scraping latest article...")
        article = scrape_latest_articles()
        if not article:
            logging.warning("No article found during scraping.")
            return False, "No article scraped"

        title = article.get("title")
        content = article.get("content")
        link = article.get("link")
        logging.info(f"Fetched article: {title}")

        success, result = process_article(title, content, link)
        if success:
            logging.info(f"Article published: {result}")
        else:
            logging.error(f"Failed to process article: {result}")
        return success, result

    except Exception as e:
        logging.exception("Unexpected error in pipeline")
        return False, str(e)
