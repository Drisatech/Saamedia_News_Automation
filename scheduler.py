import time
import schedule
import logging
from NewsCrew import run_news_pipeline
from config import SCRAPE_INTERVAL_MINUTES

# Configure logging
logging.basicConfig(
    filename='scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def job():
    logging.info("⏳ Scheduled job started")
    success, response = run_news_pipeline()
    if success:
        logging.info(f"✅ News published successfully: {response}")
    else:
        logging.error(f"❌ News publishing failed: {response}")

def start_scheduler():
    logging.info(f"🗓️ Scheduler initialized. Running every {SCRAPE_INTERVAL_MINUTES} minutes.")
    schedule.every(SCRAPE_INTERVAL_MINUTES).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    start_scheduler()