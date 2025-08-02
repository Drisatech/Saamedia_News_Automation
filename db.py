# db.py

import sqlite3
from datetime import datetime

DB_NAME = "saamedia_articles.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_articles_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            content TEXT,
            source TEXT,
            category TEXT,
            image_url TEXT,
            created_at TEXT
        )
        """)
        conn.commit()

def insert_article(title, content, source, category=None, image_url=None):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO articles 
                (title, content, source, category, image_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, content, source, category, image_url, datetime.utcnow().isoformat()))
            conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error inserting article: {e}")
        return False

def get_all_articles():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, category, source, created_at FROM articles
            ORDER BY created_at DESC
        """)
        return cursor.fetchall()

def search_articles(query=None, category=None):
    with connect_db() as conn:
        cursor = conn.cursor()
        sql = "SELECT id, title, category, source, created_at FROM articles WHERE 1=1"
        params = []

        if query:
            sql += " AND title LIKE ?"
            params.append(f"%{query}%")
        if category:
            sql += " AND category = ?"
            params.append(category)

        sql += " ORDER BY created_at DESC"
        cursor.execute(sql, params)
        return cursor.fetchall()

def get_article_by_id(article_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM articles WHERE id = ?
        """, (article_id,))
        return cursor.fetchone() 

def get_articles_by_search(query="", category=""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql = "SELECT * FROM articles WHERE 1=1"
    params = []

    if query:
        sql += " AND (title LIKE ? OR content LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])

    if category:
        sql += " AND category = ?"
        params.append(category)

    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()

    return [dict(zip(["id", "title", "content", "source", "category", "image_url", "created_at"], row)) for row in rows]