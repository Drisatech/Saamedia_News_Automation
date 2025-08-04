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
import mimetypes
import datetime

def get_category_id_by_name(category_name, WORDPRESS_REST_URL, auth):
    # Get all categories and find the ID for the given name
    resp = requests.get(f"{WORDPRESS_REST_URL}/categories?search={category_name}", auth=auth)
    if resp.status_code == 200 and resp.json():
        return resp.json()[0]['id']
    # If not found, create the category
    create_resp = requests.post(f"{WORDPRESS_REST_URL}/categories", json={"name": category_name}, auth=auth)
    if create_resp.status_code == 201:
        return create_resp.json()['id']
    return None

def publish_to_wordpress(title, content, image_url=None, category_name=None, tags=None):
    auth = (WP_USERNAME, WP_APP_PASSWORD)
    posts_url = f"{WORDPRESS_REST_URL}/posts"

    # Step 1: Upload the image and get its media ID
    featured_media_id = None
    if image_url:
        img_data = requests.get(image_url).content
        filename = image_url.split("/")[-1]
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "image/jpeg"
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

    # Step 2: Get category ID from name
    category_id = None
    if category_name:
        category_id = get_category_id_by_name(category_name, WORDPRESS_REST_URL, auth)

    # Step 3: Publish the post with full content and featured image
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

def scrape_latest_articles(source, max_articles=5):
    articles = []
    visited_links = set()
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        resp = requests.get(source, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Adjust selector for your news source
        post_links = soup.find_all("h2", class_="post-title")
        count = 0

        for post in post_links:
            if count >= max_articles:
                break
            a_tag = post.find("a")
            if not a_tag or not a_tag.get("href"):
                continue

            full_link = a_tag["href"]
            if full_link in visited_links:
                continue

            visited_links.add(full_link)
            title = a_tag.get_text(strip=True)

            # Fetch the article page and extract content and featured image
            article_content = ""
            image_url = None
            try:
                article_resp = requests.get(full_link, headers=headers, timeout=10)
                article_soup = BeautifulSoup(article_resp.text, 'html.parser')
                paragraphs = article_soup.find_all("p")
                article_content = "\n".join(
                    p.get_text() for p in paragraphs if len(p.get_text()) > 60
                )
                # Try to find a featured image
                img_tag = article_soup.find("img")
                if img_tag and img_tag.get("src"):
                    image_url = img_tag["src"]
                    if image_url.startswith("/"):
                        image_url = urljoin(source, image_url)
            except Exception as e:
                logging.warning(f"❌ Failed to fetch article content from {full_link}: {e}")

            if title and full_link and article_content:
                articles.append({
                    "title": title,
                    "content": article_content,
                    "category": "Channelstv",
                    "source": source,
                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "image_url": image_url,
                    "link": full_link
                })
                count += 1

    except Exception as e:
        logging.error(f"Error scraping articles from {source}: {e}")

    return articles