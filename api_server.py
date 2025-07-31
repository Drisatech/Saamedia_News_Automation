
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from NewsAgent import process_article
from NewsTools import init_db
import sqlite3

app = FastAPI()

async def lifespan(app: FastAPI):
    # startup logic here
    yield
    # shutdown logic (optional)

@app.get("/")
def read_root():
    return {"status": "SaaMedia NewsBot is running."}

@app.get("/run-news")
def run_news():
    # Dummy article for test
    title = "Nigeria GDP rises 3.5% in Q2 2025"
    content = "The National Bureau of Statistics has reported..."
    link = "https://example.com/gdp-news"

    success, url = process_article(title, content, link)
    return {
        "success": success,
        "url": url if success else "Error processing article"
    }

@app.get("/dashboard")
def dashboard():
    return {
        "message": "Welcome to SaaMedia NewsBot Dashboard",
        "endpoints": {
            "/": "Status check",
            "/run-news": "Trigger news sourcing + publishing",
            "/monitor": "View posted articles in HTML"
        }
    }

@app.get("/monitor", response_class=HTMLResponse)
def monitor():
    conn = sqlite3.connect("articles_log.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, category, url, created_at FROM articles ORDER BY created_at DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()

    html = """
    <html>
    <head><title>NewsBot Dashboard</title></head>
    <body style="font-family:sans-serif">
    <h2>SaaMedia NewsBot Monitor</h2>
    <table border='1' cellpadding='8' cellspacing='0'>
    <tr><th>Title</th><th>Category</th><th>URL</th><th>Created At</th></tr>
    """

    for title, cat, url, time in rows:
        html += f"<tr><td>{title}</td><td>{cat}</td><td><a href='{url}' target='_blank'>Link</a></td><td>{time}</td></tr>"

    html += "</table></body></html>"
    return html

from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import sqlite3
import os

# Setup Jinja2 environment
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

@app.get("/dashboard", response_class=HTMLResponse)
def view_dashboard():
    # Connect to the SQLite DB
    conn = sqlite3.connect("news_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, category, source_url, created_at FROM news ORDER BY created_at DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()

    # Map to dictionaries for Jinja2
    articles = [
        {
            "title": row[0],
            "category": row[1],
            "source": row[2],
            "created_at": row[3]
        }
        for row in rows
    ]

    # Render the HTML
    template = env.get_template("dashboard.html")
    html_content = template.render(articles=articles)

    return HTMLResponse(content=html_content)
