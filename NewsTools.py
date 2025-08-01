import sqlite3
import requests
from config import (
    WORDPRESS_REST_URL,
    WP_USERNAME,
    WP_APP_PASSWORD,
    WHATSAPP_PHONE,
    WHATSAPP_API,
    DATABASE_FILE
)
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import base64


def publish_to_wordpress(title, content, category):
    """Publishes a post to WordPress using the REST API."""
    try:
        # Prepare authentication
        credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
        token = base64.b64encode(credentials.encode())
        headers = {
            "Authorization": f"Basic {token.decode('utf-8')}",
            "Content-Type": "application/json"
        }

        # Optional: fetch or create category via REST API
        cat_resp = requests.get(f"{WORDPRESS_REST_URL}/categories?search={category}", headers=headers)
        cat_resp.raise_for_status()
        categories = cat_resp.json()

        if categories:
            category_id = categories[0]['id']
        else:
            new_cat_resp = requests.post(
                f"{WORDPRESS_REST_URL}/categories",
                headers=headers,
                json={"name": category}
            )
            new_cat_resp.raise_for_status()
            category_id = new_cat_resp.json()['id']

        # Create post
        post_data = {
            "title": title,
            "content": content,
            "status": "publish",
            "categories": [category_id]
        }

        post_resp = requests.post(f"{WORDPRESS_REST_URL}/posts", headers=headers, json=post_data)
        post_resp.raise_for_status()
        post_url = post_resp.json().get("link")
        print(f"✅ Published: {post_url}")
        return post_url

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


# scrape_latest_articles

logging.basicConfig(
    filename="newstools.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def scrape_latest_articles():
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

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }

    articles = []
    visited_links = set()

    for source, selector in sources.items():
        try:
            response = requests.get(source, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.select(selector)

            count = 0
            for link_tag in links:
                href = link_tag.get("href")
                if not href:
                    continue

                full_link = urljoin(source, href)
                if full_link in visited_links:
                    continue

                visited_links.add(full_link)
                title = link_tag.get_text(strip=True)

                if title and full_link:
                    articles.append({
                        "title": title,
                        "link": full_link,
                        "content": f"Full content to be fetched from {full_link}"  # Placeholder
                    })
                    count += 1

                if count >= 5:
                    break

            logging.info(f"✅ Scraped {count} articles from {source}")

        except requests.exceptions.RequestException as e:
            logging.warning(f"❌ Failed to scrape {source}: {e}")
            continue

    return articles
