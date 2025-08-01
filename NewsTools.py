import xmlrpc.client
import sqlite3
import requests
from config import WORDPRESS_XMLRPC, WP_USERNAME, WP_PASSWORD, WHATSAPP_PHONE, WHATSAPP_API, DATABASE_FILE

def publish_to_wordpress(title, content, category):
    """Publishes a post to WordPress using XML-RPC."""
    try:
        server = xmlrpc.client.ServerProxy(WORDPRESS_XMLRPC)
        post = {
            'title': title,
            'description': content,
            'categories': [category],
            'post_type': 'post'
        }
        post_id = server.metaWeblog.newPost('', WP_USERNAME, WP_PASSWORD, post, True)
        return f"{WORDPRESS_XMLRPC.replace('xmlrpc.php', '')}?p={post_id}"
    except Exception as e:
        print(f"❌ WordPress publish error: {e}")
        return None

def log_article(title, category, url, status):
    """Logs published article into SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                category TEXT,
                url TEXT,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('INSERT INTO articles (title, category, url, status) VALUES (?, ?, ?, ?)',
                       (title, category, url, status))
        conn.commit()
        conn.close()
        print("✅ Article logged successfully.")
    except Exception as e:
        print(f"❌ Logging error: {e}")

def notify_whatsapp(message):
    """Sends WhatsApp alert using CallMeBot."""
    try:
        url = f"{WHATSAPP_API}&text={message}"
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ WhatsApp notification sent.")
        else:
            print(f"❌ WhatsApp response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ WhatsApp alert error: {e}")


from bs4 import BeautifulSoup

def scrape_latest_articles():
    """
    Scrapes the latest news articles from multiple Nigerian news sources.
    Returns a list of dictionaries with keys: 'title', 'url', 'content', 'source'
    """
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

    scraped_articles = []

    for base_url, selector in sources.items():
        try:
            response = requests.get(base_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.select(selector)

            for link_tag in links[:3]:  # get up to 3 articles per source
                try:
                    title = link_tag.text.strip()
                    url = link_tag.get("href")

                    # Normalize relative URLs
                    if url and url.startswith("/"):
                        url = base_url.rstrip("/") + url

                    if not url or not url.startswith("http"):
                        continue

                    article_response = requests.get(url, timeout=10)
                    article_response.raise_for_status()

                    article_soup = BeautifulSoup(article_response.content, 'html.parser')
                    paragraphs = article_soup.select('p')
                    content = '\n'.join(p.get_text(strip=True) for p in paragraphs[:5])

                    if len(content) > 100:
                        scraped_articles.append({
                            "title": title,
                            "url": url,
                            "content": content,
                            "source": base_url
                        })

                except Exception as inner_e:
                    print(f"⚠️ Error scraping article from {base_url}: {inner_e}")

        except Exception as outer_e:
            print(f"❌ Failed to scrape {base_url}: {outer_e}")

    return scraped_articles
