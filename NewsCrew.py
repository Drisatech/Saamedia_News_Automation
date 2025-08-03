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
            return []

        processed_articles = []

        for article in articles:
            title = article.get("title")
            content = article.get("content")
            link = article.get("link")
            image_url = article.get("image_url", "")  # Optional field

            if not all([title, content, link]):
                logging.warning("Incomplete article skipped.")
                continue

            logging.info(f"Processing article: {title}")
            result = process_article(title, content, link, image_url=image_url)

            if result:
                try:
                    # After scraping:
                    title = result['title']
                    full_content = result['summary']  # Make sure this is the full HTML/text
                    image_url = result.get('image_url', '')   # Main/featured image URL

                    publish_to_wordpress(title, full_content, image_url)

                    log_article(result)
                    if ENABLE_WHATSAPP_ALERTS:
                        notify_whatsapp(result)
                    logging.info(f"✅ Article published: {result['title']}")

                    # Append processed article (for dashboard or scheduler)
                    processed_articles.append({
                        "title": result["title"],
                        "content": result["summary"],  # Can switch to full content if preferred
                        "category": result["category"],
                        "link": link,
                        "image_url": image_url
                    })
                except Exception as e:
                    logging.error(f"❌ Failed to publish/log/notify for article: {e}")
            else:
                logging.error("❌ Article processing failed.")

        logging.info(f"{len(processed_articles)} article(s) successfully processed and published.")
        return processed_articles

    except Exception as e:
        logging.exception("❌ Unexpected error in news pipeline.")
        return []