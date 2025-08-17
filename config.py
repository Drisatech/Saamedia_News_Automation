from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🌐 WordPress REST-URL Settings
WORDPRESS_REST_URL = "https://saamedia.info/wp-json/wp/v2"
WP_USERNAME = "SAAMEDIA.INFO"
WP_APP_PASSWORD = "WP_APP_PASSWORD"

# 📞 WhatsApp Alert Config via CallMeBot
WHATSAPP_API = "https://api.callmebot.com/whatsapp.php?phone=2348060466910&text=This+is+a+test&apikey=6321397"
WHATSAPP_PHONE = "+2348060466910"
ENABLE_WHATSAPP_ALERTS = True # or False

# 📁 News Categories
CATEGORIES = [
    "The Nation",
    "Politics",
    "Business & Economy",
    "Corruption",
    "Crime & Security",
    "Sports",
    "Entertainment",
    "Kogi News",
    "Featured"
]

# 📅 Scheduler Settings
SCRAPE_INTERVAL_MINUTES = 60

# 🧠 AI Settings
LLM_MODEL_NAME = "openrouter/openai/gpt-3.5-turbo"  # <- openrouter format
TEMPERATURE = 0.3

# 🗂️ SQLite DB Name
DATABASE_FILE = "news_history.db"

