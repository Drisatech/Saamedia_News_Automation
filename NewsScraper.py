import requests
from bs4 import BeautifulSoup
from NewsAgent import process_article

sources = {
    "https://www.channelstv.com": "div.post-item a",
    "https://www.punchng.com": "h2.post-title a",
    "https://tvcnews.tv": "h2.entry-title a",
    "https://nairametrics.com": "h2.post-title a",
    "https://dailytrust.com": "div.td-module-thumb a",
    "https://businessday.ng": "h3.entry-title a",
    "https://www.arise.tv": "h3 a",
    "https://www.premiumtimesng.com": "h2.post-title a"
}

def scrape_and_process():
    for site, selector in sources.items():
        try:
            html = requests.get(site, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")
            articles = soup.select(selector)

            for article in articles[:2]:  # Limit scraping
                title = article.text.strip()
                link = article.get("href")
                if not link.startswith("http"):
                    link = site + link

                article_html = requests.get(link, timeout=10).text
                article_soup = BeautifulSoup(article_html, "html.parser")
                paragraphs = article_soup.find_all("p")
                content = "\n".join(p.get_text() for p in paragraphs if len(p.get_text()) > 60)

                if len(content) < 200:
                    continue

                success, result = process_article(title, content, link)
                print(f"[{'✅' if success else '❌'}] {title} -> {result}")

        except Exception as e:
            print(f"[ERROR] Could not fetch from {site}: {e}")
