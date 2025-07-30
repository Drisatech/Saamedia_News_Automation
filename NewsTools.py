
import os
import sqlite3
import requests
from urllib.parse import quote
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from dotenv import load_dotenv
from crewai_tools import ScrapeWebsiteTool

# Load environment variables
load_dotenv()

categorize_tool = ScrapeWebsiteTool(
    website_url="https://saamedia.info/",
    tool_name="CategorizeTool",
    description="Tool for scraping and analyzing categories from Nigerian news articles"
)

summarize_tool = ScrapeWebsiteTool(
    website_url="https://saamedia.info/",
    tool_name="SummarizeTool",
    description="Tool for summarizing Nigerian news articles"
)

# WordPress setup from environment variables
wp_url = os.getenv('WP_URL')
wp_username = os.getenv('WP_USERNAME')
wp_password = os.getenv('WP_PASSWORD')

# Database configuration
database_name = os.getenv('DATABASE_NAME', 'articles_log.db')

# WhatsApp configuration
whatsapp_phone = os.getenv('WHATSAPP_PHONE_NUMBER')
whatsapp_api_key = os.getenv('WHATSAPP_API_KEY')

# Validate required environment variables
required_vars = ['WP_URL', 'WP_USERNAME', 'WP_PASSWORD']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"Warning: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file")

try:
    if all([wp_url, wp_username, wp_password]):
        client = Client(wp_url, wp_username, wp_password)
    else:
        client = None
        print("WordPress client not initialized due to missing credentials")
except Exception as e:
    print(f"Failed to initialize WordPress client: {e}")
    client = None

def publish_to_wordpress(title, content, category):
    """
    Publish an article to WordPress
    
    Args:
        title (str): Article title
        content (str): Article content
        category (str): Article category
        
    Returns:
        str: URL of published post or error message
    """
    if not client:
        return "WordPress client not initialized - check environment variables"
    
    try:
        post = WordPressPost()
        post.title = title
        post.content = content
        post.terms_names = {
            'category': [category]
        }
        post.post_status = 'publish'
        post_id = client.call(NewPost(post))
        
        # Extract base URL from wp_url for constructing post URL
        base_url = wp_url.replace('/xmlrpc.php', '')
        return f"{base_url}/?p={post_id}"
    except Exception as e:
        return f"Failed to publish to WordPress: {e}"

# SQLite Logging
def init_db():
    """Initialize the SQLite database for article logging"""
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            url TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        return False

def log_article(title, category, url, status):
    """
    Log article information to SQLite database
    
    Args:
        title (str): Article title
        category (str): Article category
        url (str): Article URL
        status (str): Article status
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO articles (title, category, url, status) VALUES (?, ?, ?, ?)",
            (title, category, url, status)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database logging error: {e}")
        return False

# WhatsApp Notifier (CallMeBot)
def notify_whatsapp(message, phone_number=None, api_key=None):
    """
    Send WhatsApp notification via CallMeBot API
    
    Args:
        message (str): Message to send
        phone_number (str, optional): Phone number with country code
        api_key (str, optional): CallMeBot API key
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Use provided parameters or fall back to environment variables
    phone = phone_number or whatsapp_phone
    key = api_key or whatsapp_api_key
    
    if not phone or not key:
        print("WhatsApp phone number or API key not configured")
        return False
    
    try:
        # Use urllib.parse.quote instead of requests.utils.quote
        encoded_msg = quote(message)
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_msg}&apikey={key}"
        
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"WhatsApp notification error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error in WhatsApp notification: {e}")
        return False

def get_article_stats():
    """
    Get statistics about logged articles
    
    Returns:
        dict: Article statistics or None if error
    """
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM articles")
        total = cursor.fetchone()[0]
        
        # Get count by status
        cursor.execute("SELECT status, COUNT(*) FROM articles GROUP BY status")
        status_counts = dict(cursor.fetchall())
        
        # Get count by category
        cursor.execute("SELECT category, COUNT(*) FROM articles GROUP BY category")
        category_counts = dict(cursor.fetchall())
        
        # Get recent articles
        cursor.execute("SELECT title, category, status, created_at FROM articles ORDER BY created_at DESC LIMIT 10")
        recent_articles = cursor.fetchall()
        
        conn.close()
        
        return {
            'total': total,
            'by_status': status_counts,
            'by_category': category_counts,
            'recent': recent_articles
        }
    except sqlite3.Error as e:
        print(f"Error getting article stats: {e}")
        return None

def check_configuration():
    """
    Check if all required configurations are present
    
    Returns:
        dict: Configuration status
    """
    config_status = {
        'wordpress': bool(wp_url and wp_username and wp_password),
        'whatsapp': bool(whatsapp_phone and whatsapp_api_key),
        'database': bool(database_name),
        'openai': bool(os.getenv('OPENAI_API_KEY'))
    }
    
    return config_status

# Initialize database on import
if __name__ == "__main__":
    print("Initializing database...")
    if init_db():
        print("Database initialized successfully")
    else:
        print("Failed to initialize database")
    
    print("\nConfiguration status:")
    config = check_configuration()
    for service, status in config.items():
        status_text = "✓ Configured" if status else "✗ Not configured"
        print(f"{service.capitalize()}: {status_text}")