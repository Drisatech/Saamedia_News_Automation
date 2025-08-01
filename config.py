from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🌐 WordPress REST-URL Settings
WORDPRESS_REST_URL = "https://saamedia.info/wp-json/wp/v2"
WP_USERNAME = "SAAMEDIA.INFO"
WP_APP_PASSWORD = "OQFk WB6F WyVq 6Klo v3rp XIvd"

# 📞 WhatsApp Alert Config via CallMeBot
WHATSAPP_API = "https://api.callmebot.com/whatsapp.php?phone=2348121044557&text=This+is+a+test&apikey=2254657"
WHATSAPP_PHONE = "+2348121044557"
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
SCRAPE_INTERVAL_MINUTES = 30

# 🧠 AI Settings
LLM_MODEL_NAME = "openrouter/openai/gpt-3.5-turbo"  # <- openrouter format
TEMPERATURE = 0.3

# 🗂️ SQLite DB Name
DATABASE_FILE = "news_history.db"