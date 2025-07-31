from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from NewsAgent import process_article
from NewsTools import init_db
import sqlite3
import os

# --- App Setup ---
app = FastAPI()

# --- Jinja2 Template Setup ---
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

# --- FastAPI Routes ---

@app.get("/")
def read_root():
    return {"status": "✅ SaaMedia NewsBot is running."}

@app.get("/run-news")
def run_news():
    # Dummy article for test
    title = "Nigeria GDP rises 3.5% in Q2 2025"
    content = "The National Bureau of Statistics has reported..."
    link = "https://example.com/gdp-news"

    success, url = process_article(title, content, link)
    return {
        "success": success,
        "url": url if success else "❌ Error processing article"
    }

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    conn = sqlite3.connect("articles_log.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, category, url, created_at FROM articles ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    articles = [
        {
            "title": row[0],
            "category": row[1],
            "source": row[2],
            "created_at": row[3]
        }
        for row in rows
    ]
    return templates.TemplateResponse("dashboard.html", {"request": request, "articles": articles})

@app.get("/endpoints")
def show_endpoints():
    return {
        "endpoints": {
            "/": "Check status",
            "/run-news": "Trigger dummy news post",
            "/dashboard": "HTML table of last 50 articles",
            "/endpoints": "This help listing"
        }
    }

