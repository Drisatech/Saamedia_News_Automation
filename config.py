# config.py

import os

openai_api_key = os.getenv("OPENAI_API_KEY")

# 🔐 OpenAI Key
OPENAI_API_KEY = "sk-your-key-here"

# 🌐 WordPress XML-RPC Settings
WORDPRESS_XMLRPC = "https://saamedia.info/xmlrpc.php"
WP_USERNAME = "SAAMEDIA.INFO"
WP_PASSWORD = "OQFk WB6F WyVq 6Klo v3rp XIvd"

# 📞 WhatsApp Alert Config via CallMeBot
WHATSAPP_API = "https://api.callmebot.com/whatsapp.php?phone=2348121044557&text=This+is+a+test&apikey=2254657"
WHATSAPP_PHONE = "+2348121044557"  # Your verified phone number with CallMeBot

# 📁 News Categories
CATEGORIES = [
    "The Nation",
    "Politics",
    "Business & Economy",
    "Corruption",
    "Crime & Security",
    "Sports",
    "Entertainment"
    "Kogi News"
    "Featured"
    ]

# 📅 Scheduler Settings
SCRAPE_INTERVAL_MINUTES = 30

# 🧠 AI Settings
LLM_MODEL_NAME = "gpt-3.5-turbo"  # or gpt-4
TEMPERATURE = 0.5

# 🗂️ SQLite DB Name
DATABASE_FILE = "news_history.db"
