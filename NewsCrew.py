# NewsCrew.py

import logging
from NewsTasks import get_categorize_task, get_summarize_task
from NewsAgent import categorizer_agent, summarizer_agent, process_article
from NewsTools import (
    scrape_latest_articles,
    publish_to_wordpress,
    log_article,
    notify_whatsapp
)
from config import ENABLE_WHATSAPP_ALERTS

# Set up logging
logging.basicConfig(
    filename='newscrew.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Prepare agents and tasks (optional, in case you use them elsewhere)
agents = [categorizer_agent, summarizer_agent]
tasks = [
    get_categorize_task(categorizer_agent),
    get_summarize_task(summarizer_agent)
]

def run_news_pipeline():
    try:
        logging.info("Scraping articles from multiple news sources...")
        articles = scrape_latest_articles()

        if not articles:
            logging.warning("No articles scraped from any source.")
            return False, "No articles found."

        success_count = 0
        failure_count = 0

        for article in articles:
            title = article.get("title")
            content = article.get("content")
            link = article.get("link")

            if not all([title, content, link]):
                logging.warning("Incomplete article skipped.")
                continue

            logging.info(f"Processing article: {title}")
            result = process_article(title, content, link)

            if result:
                try:
                    publish_to_wordpress(result["title"], result["summary"], result["category"])
                    log_article(result)
                    if ENABLE_WHATSAPP_ALERTS:
                        notify_whatsapp(result)
                    logging.info(f"✅ Article published: {result['title']}")
                    success_count += 1
                except Exception as e:
                    logging.error(f"❌ Failed to publish/log/notify for article: {e}")
                    failure_count += 1
            else:
                logging.error("❌ Article processing failed.")
                failure_count += 1

        summary_msg = f"{success_count} article(s) published, {failure_count} failed."
        logging.info(summary_msg)

        return True, summary_msg

    except Exception as e:
        logging.exception("❌ Unexpected error in news pipeline.")
        return False, str(e)
