import time
import traceback
from NewsCrew import run_news_pipeline
from NewsAgent import process_article

def main():
    print("Starting SaaMedia News Automation Scheduler...\n")

    try:
        # STEP 1: Run the full news pipeline
        results = run_news_pipeline()

        print(f"\n{len(results)} articles processed by CrewAI.\n")

        for article in results:
            title = article.get("title")
            content = article.get("content")
            category = article.get("category", "Uncategorized")
            link = article.get("link")
            image_url = article.get("image_url")  # Optional: image from feed or scraping

            if title and content:
                print(f"Posting article: {title}")
                success, message = process_article(
                    title=title,
                    content=content,
                    category=category,
                    link=link,
                    image_url=image_url
                )
                print(f"Status: {'✅ Success' if success else '❌ Failed'} | {message}")
            else:
                print("Skipping invalid article (missing title or content).")

    except Exception as e:
        print("Scheduler failed due to error:")
        traceback.print_exc()

if __name__ == "__main__":
    # Run every 60 minutes
    while True:
        main()
        print("Sleeping for 60 minutes...\n")
        time.sleep(1800)  # 3600 seconds = 60 minutes