import sqlite3
import requests
from config import (
    WORDPRESS_REST_URL,  # e.g., "https://saamedia.info/wp-json/wp/v2"
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

def publish_to_wordpress(title, content, category, image_url):
    """Publish a post to WordPress via the REST API."""
    try:
        # Create authentication header
        credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }

        # Use the correct REST URL from config
        site_url = WORDPRESS_REST_URL.replace("/wp-json/wp/v2", "")

        # Get category ID (or create if not exists)
        cat_response = requests.get(
            f"{site_url}/wp-json/wp/v2/categories?search={category}", headers=headers)
        cat_response.raise_for_status()
        cat_data = cat_response.json()

        if cat_data:
            category_id = cat_data[0]['id']
        else:
            # Create new category
            create_cat = requests.post(
                f"{site_url}/wp-json/wp/v2/categories",
                headers=headers,
                json={"name": category}
            )
            create_cat.raise_for_status()
            category_id = create_cat.json()['id']

        # Prepare post payload
        post_data = {
            'title': title,
            'content': content,
            'status': 'publish',
            'categories': [category_id],
        }
        # Optionally add image_url as a custom field or featured_media if supported
        if image_url:
            post_data['meta'] = {'image_url': image_url}

        post_url = f"{site_url}/wp-json/wp/v2/posts"
        response = requests.post(post_url, headers=headers, json=post_data)
        response.raise_for_status()

        return response.json().get('link')  # Return published URL

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