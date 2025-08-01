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

logging.basicConfig(
    filename='newscrew.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

agents = [categorizer_agent, summarizer_agent]
tasks = [
    get_categorize_task(categorizer_agent),
    get_summarize_task(summarizer_agent)
]

def run_news_pipeline():
    try:
        logging.info("🔍 Scraping latest articles from sources...")
        articles = scrape_latest_articles()
        if not articles:
            logging.warning("❌ No articles scraped.")
            return False, "No articles found"

        results = []
        for article in articles:
            title = article.get("title")
            content = article.get("content")
            url = article.get("url")
            source = article.get("source")

            if not title or not content or not url:
                logging.warning("⚠️ Skipping incomplete article.")
                continue

            logging.info(f"📰 Processing article: {title}")
            success, processed = process_article(title, content, url)

            if not success:
                logging.error(f"❌ Processing failed: {processed}")
                continue

            summary = processed.get("summary", content)
            category = processed.get("category", "Uncategorized")

            full_content = f"{summary}\n\n🔗 [Read full]({url})\n📡 Source: {source}"
            wp_url = publish_to_wordpress(title, full_content, category)

            if wp_url:
                log_article(title, category, wp_url, status="Published")

                if ENABLE_WHATSAPP_ALERTS:
                    notify_whatsapp(f"✅ *{title}* just got published!\n🔗 {wp_url}")

                results.append({
                    "title": title,
                    "category": category,
                    "url": wp_url,
                    "source": source
                })
            else:
                logging.error("❌ Failed to publish article to WordPress.")

        return True, results if results else "No articles published"

    except Exception as e:
        logging.exception("🔥 Exception in run_news_pipeline")
        return False, str(e)
