import sqlite3
import requests
import logging
import base64
import mimetypes
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import (
    WORDPRESS_REST_URL,  # e.g., "https://saamedia.info/wp-json/wp/v2"
    WP_USERNAME,
    WP_APP_PASSWORD,
    WHATSAPP_PHONE,
    WHATSAPP_API,
    DATABASE_FILE
)

# ---------- WORDPRESS PUBLISHING ---------- #

def get_category_id_by_name(category_name, base_url, auth):
    """Get or create a WordPress category by name and return its ID."""
    resp = requests.get(f"{base_url}/categories?search={category_name}", auth=auth)
    if resp.status_code == 200 and resp.json():
        return resp.json()[0]['id']
    
    # Create the category if not found
    create_resp = requests.post(f"{base_url}/categories", json={"name": category_name}, auth=auth)
    if create_resp.status_code == 201:
        return create_resp.json()['id']
    
    return None


def publish_to_wordpress(title, content, image_url=None, category_name=None, tags=None):
    """Publishes article to WordPress site with optional image and category."""
    auth = (WP_USERNAME, WP_APP_PASSWORD)
    posts_url = f"{WORDPRESS_REST_URL}/posts"
    featured_media_id = None

    # Use logo if no image_url provided
    if not image_url:
        image_url = "https://saamedia.info/wp-content/uploads/2024/02/SAAMEDIA-Logo-2.jpg"

    # Upload image
    try:
        img_data = requests.get(image_url).content
        filename = image_url.split("/")[-1]
        mime_type, _ = mimetypes.guess_type(filename) or ("image/jpeg", None)
        media_headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": mime_type
        }
        media_resp = requests.post(
            f"{WORDPRESS_REST_URL}/media",
            headers=media_headers,
            data=img_data,
            auth=auth,
        )
        if media_resp.status_code == 201:
            featured_media_id = media_resp.json().get("id")
    except Exception as e:
        logging.warning(f"❌ Failed to upload image: {e}")

    # Get category ID
    category_id = None
    if category_name:
        category_id = get_category_id_by_name(category_name, WORDPRESS_REST_URL, auth)

    # Prepare post data
    post_data = {
        "title": title,
        "content": content,
        "status": "publish",
    }
    if featured_media_id:
        post_data["featured_media"] = featured_media_id
    if category_id:
        post_data["categories"] = [category_id]
    if tags:
        post_data["tags"] = tags

    resp = requests.post(posts_url, json=post_data, auth=auth)
    return resp

# ---------- LOGGING TO DATABASE ---------- #

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

# ---------- WHATSAPP ALERT ---------- #

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

# ---------- LOGGING CONFIG ---------- #

logging.basicConfig(
    filename="newstools.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------- SCRAPE LATEST ARTICLES ---------- #

def scrape_latest_articles(max_articles=5):
    sources = {
        "https://www.channelstv.com/category/politics/": "h3 a",
        "https://nairametrics.com/category/nigeria-business-news": "h3 a",
        "https://www.arise.tv/category/global": "h3 a",
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    all_articles = []

    for source, selector in sources.items():
        visited_links = set()
        count = 0
        try:
            resp = requests.get(source, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            post_links = soup.select(selector)

            for a_tag in post_links:
                if count >= max_articles:
                    break

                href = a_tag.get("href")
                if not href or href in visited_links:
                    continue

                visited_links.add(href)
                title = a_tag.get_text(strip=True)

                # Fetch article page
                article_content = ""
                image_url = None
                try:
                    article_resp = requests.get(href, headers=headers, timeout=10)
                    article_soup = BeautifulSoup(article_resp.text, 'html.parser')
                    paragraphs = article_soup.find_all("p")
                    article_content = "\n".join(
                        p.get_text() for p in paragraphs if len(p.get_text()) > 60
                    )

                    # Try featured image
                    img_tag = article_soup.find("img")
                    if img_tag and img_tag.get("src"):
                        image_url = img_tag["src"]
                        if image_url.startswith("/"):
                            image_url = urljoin(source, image_url)
                except Exception as e:
                    logging.warning(f"❌ Failed to fetch article from {href}: {e}")
                    continue

                if title and article_content:
                    # Add acknowledgement credit at the bottom
                    credit_line = f"\n\n---\n*Source: [{source}]({source})*"
                    article_content += credit_line

                    all_articles.append({
                        "title": title,
                        "content": article_content,
                        "category": source.split("//")[1].split(".")[0].capitalize(),
                        "source": source,
                        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "image_url": image_url,
                        "link": href
                    })
                    count += 1

            logging.info(f"✅ Scraped {count} articles from {source}")

        except requests.exceptions.RequestException as e:
            logging.warning(f"❌ Failed to scrape {source}: {e}")
            continue

    return all_articles




