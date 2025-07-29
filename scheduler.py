# scheduler.py

from apscheduler.schedulers.blocking import BlockingScheduler
from NewsCrew import scrape_and_process

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', minutes=30)
def run_job():
    print("🔁 Running scheduled scraping + posting...")
    scrape_and_process()

if __name__ == "__main__":
    print("📆 Starting SaaMedia News Scheduler...")
    scheduler.start()
