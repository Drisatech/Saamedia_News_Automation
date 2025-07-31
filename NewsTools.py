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