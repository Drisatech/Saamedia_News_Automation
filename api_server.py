#api_server.py

from flask import Flask, jsonify
from NewsAgent import process_article
from NewsCrew import scrape_latest_articles

import traceback

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "🚀 SaaMedia News Automation API is running"})

@app.route("/run-news", methods=["GET"])
def run_news():
    try:
        articles = scrape_latest_articles()

        if not articles:
            return jsonify({"success": False, "url": "❌ No new articles found"})

        total = len(articles)
        success_count = 0
        failures = []

        for article in articles:
            title = article.get("title")
            content = article.get("content")
            link = article.get("link")

            success, result = process_article(title, content, link)

            if success:
                success_count += 1
            else:
                failures.append({
                    "title": title,
                    "error": result
                })

        if success_count == total:
            return jsonify({"success": True, "url": f"✅ All {total} articles processed successfully!"})
        elif success_count > 0:
            return jsonify({
                "success": True,
                "url": f"⚠️ {success_count}/{total} articles processed. Some failed.",
                "failures": failures
            })
        else:
            return jsonify({
                "success": False,
                "url": "❌ All articles failed to process.",
                "failures": failures
            })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "url": f"❌ Server error: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True)