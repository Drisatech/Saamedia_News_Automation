import logging
from NewsAgent import process_article
from NewsTasks import scrape_latest_article

# Setup logging
logging.basicConfig(
    filename='newscrew.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_news_pipeline():
    """
    Orchestrates the scraping and processing of the latest news article.
    Returns:
        (bool, str): success flag and URL or error message.
    """
    try:
        logging.info("🔍 Scraping latest article...")
        article = scrape_latest_article()

        if not article:
            logging.warning("⚠️ No new article found.")
            return False, "No article scraped"

        title, content, link = article["title"], article["content"], article["link"]
        logging.info(f"📰 Article fetched: {title}")

        success, result = process_article(title, content, link)

        if success:
            logging.info(f"✅ Article published successfully: {result}")
        else:
            logging.error(f"❌ Article processing failed: {result}")

        return success, result

    except Exception as e:
        logging.exception("💥 Unexpected error during news pipeline execution")
        return False, str(e)