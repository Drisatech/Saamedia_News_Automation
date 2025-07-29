# NewsTools.py
import sqlite3
import requests
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

# WordPress setup
wp_url = "https://saamedia.info/xmlrpc.php"
wp_username = "SAAMEDIA.INFO"  # replace
wp_password = "OQFk WB6F WyVq 6Klo v3rp XIvd"  # replace

client = Client(wp_url, wp_username, wp_password)

def publish_to_wordpress(title, content, category):
    post = WordPressPost()
    post.title = title
    post.content = content
    post.terms_names = {
        'category': [category]
    }
    post.post_status = 'publish'
    post_id = client.call(NewPost(post))
    return f"https://saamedia.info/?p={post_id}"

# SQLite Logging
def init_db():
    conn = sqlite3.connect("articles_log.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        category TEXT,
        url TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def log_article(title, category, url, status):
    conn = sqlite3.connect("articles_log.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO articles (title, category, url, status) VALUES (?, ?, ?, ?)",
        (title, category, url, status)
    )
    conn.commit()
    conn.close()

# WhatsApp Notifier (CallMeBot)
def notify_whatsapp(phone_number, api_key, message):
    encoded_msg = requests.utils.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={encoded_msg}&apikey={api_key}"
    res = requests.get(url)
    return res.status_code == 200
