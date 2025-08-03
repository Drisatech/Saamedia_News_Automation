from flask import Flask, jsonify, render_template  # ✅ Added render_template
from NewsAgent import process_article
from NewsCrew import scrape_latest_articles
import traceback
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "🚀 SaaMedia News Automation API is running"})

@app.route("/docs")
def api_docs():
    return render_template("docs.html")

@app.route("/status")
def status():
    return jsonify({"status": "ok", "message": "API is healthy ✅"})

@app.route("/dashboard")
def dashboard():
    # Fetch articles for the dashboard
    articles = scrape_latest_articles() or []
    return render_template("dashboard.html", articles=articles)

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

            try:
                result = process_article(title, content, link)
                if isinstance(result, tuple) and len(result) == 2:
                    success, message = result
                else:
                    success, message = False, "Invalid response format from process_article"

                if success:
                    success_count += 1
                else:
                    failures.append({"title": title, "error": message})
            except Exception as inner_error:
                failures.append({"title": title, "error": str(inner_error)})

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)