# api_server.py
from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from NewsCrew import run_news_scraper
from NewsAgent import process_article
from NewsCrew import scrape_latest_articles
import traceback

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "🚀 SaaMedia News Automation API is running"})

@app.route("/status")
def status():
    return jsonify({"status": "ok", "message": "API is healthy ✅"})

app = Flask(__name__, template_folder="templates")

DB_PATH = os.path.join(os.getcwd(), "news_articles.db")

@app.route("/dashboard")
def dashboard():
    query = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    base_query = "SELECT title, category, source, created_at FROM articles"
    conditions = []
    values = []

    if query:
        conditions.append("(title LIKE ? OR content LIKE ?)")
        values.extend([f"%{query}%", f"%{query}%"])
    if category_filter:
        conditions.append("category LIKE ?")
        values.append(f"%{category_filter}%")

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY created_at DESC LIMIT 100"
    cursor.execute(base_query, values)
    rows = cursor.fetchall()
    conn.close()

    articles = [
        {"title": row[0], "category": row[1], "source": row[2], "created_at": row[3]}
        for row in rows
    ]

    return render_template("dashboard.html", articles=articles, query=query, category=category_filter)

@app.route("/docs")
def api_docs():
    return render_template("docs.html")

@app.route("/run-news")
def run_news():
    try:
        results = run_news_scraper()
        return jsonify({"status": "running", "results": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8000)