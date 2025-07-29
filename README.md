```markdown
# 📰 SaaMedia News Automation System

A multi-AI agent news automation platform that sources, summarizes, categorizes, and auto-publishes news from major Nigerian news websites to your WordPress site [saamedia.info](https://saamedia.info) with WhatsApp alerts and admin dashboard tracking — powered by [CrewAI](https://github.com/joaomdmoura/crewAI), OpenAI, and FastAPI.

---

## 🔧 Features

✅ Multi-Agent AI pipeline using [CrewAI](https://github.com/joaomdmoura/crewAI)  
✅ Auto-scraping from top Nigerian news sites  
✅ AI-powered **categorization** and **summarization**  
✅ Auto-publish to WordPress (via XML-RPC)  
✅ SQLite logging for all published news  
✅ HTML dashboard to monitor article history  
✅ WhatsApp notifier for every successful post  
✅ Scheduler: runs automatically every 30 minutes  
✅ Runs on **Railway**, works with **Termux**, no sudo/root required  

---

## 🌐 News Sources

| Site | Type |
|------|------|
| [ChannelsTV](https://www.channelstv.com) | General |
| [PunchNG](https://www.punchng.com) | National |
| [TVC News](https://www.tvcnews.tv) | National |
| [DailyTrust](https://www.dailytrust.com) | Politics/Security |
| [Arise TV](https://www.arise.tv) | Business/Politics |
| [Nairametrics](https://www.nairametrics.com) | Business |
| [BusinessDay NG](https://www.businessday.ng) | Economy |

---

## 📁 Project Structure

```

saamedia\_news\_automation/
├── NewsAgents.py              # AI agents using CrewAI
├── NewsTasks.py               # Tasks for summarizing and categorizing
├── NewsCrew\.py                # Scraper + AI + WordPress poster
├── NewsTools.py               # Utilities: SQLite, WhatsApp, WordPress XML-RPC
├── api\_server.py              # REST API (if needed)
├── scheduler.py               # APScheduler for periodic scraping
├── config.py                  # Config file (keys, URLs, etc.)
├── dashboard.html             # Lightweight HTML dashboard
├── saamedia-news-integration.php # (Optional) WordPress PHP script
├── requirements.txt
├── README.md

````

---

## 🚀 Installation Guide (Termux + Railway)

### Step 1: Setup Local Dev Env in Termux

```bash
pkg install python git
pip install virtualenv
git clone https://github.com/your-username/saamedia_news_automation.git
cd saamedia_news_automation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
````

---

### Step 2: Configure `config.py`

Edit your `config.py`:

```python
OPENAI_API_KEY = "sk-xxxx"
WORDPRESS_XMLRPC = "https://saamedia.info/xmlrpc.php"
WP_USERNAME = "your-wp-user"
WP_PASSWORD = "your-app-password"
WHATSAPP_API = "https://api.callmebot.com/whatsapp.php"
WHATSAPP_PHONE = "+234XXXXXXXXXX"
```

---

### Step 3: Run Locally

```bash
python scheduler.py
```

You’ll see:

```
📆 Starting SaaMedia News Scheduler...
🔁 Running scheduled scraping + posting...
✅ Punch headlines -> Politics
✅ TVC Business -> Business & Economy
...
```

---

### Step 4: Deploy to [Railway](https://railway.app)

#### a. Login and Initialize

```bash
railway login
railway init
```

#### b. Set Start Command in `railway.json`

```json
{
  "scripts": {
    "start": "python scheduler.py"
  }
}
```

Or for API + Scheduler:

```json
{
  "scripts": {
    "start": "gunicorn api_server:app --bind 0.0.0.0:$PORT & python scheduler.py"
  }
}
```

#### c. Push to Railway

```bash
railway up
```

---

## 🧠 AI Agent Logic (CrewAI)

* **Categorizer Agent** → Uses `gpt-3.5` to classify topics
* **Summarizer Agent** → Generates blog-friendly summary
* **CrewAI Orchestrator** → Handles sequential tasks

---

## 🧾 Categories Supported

* ✅ The Nation
* ✅ Politics
* ✅ Business & Economy
* ✅ Corruption
* ✅ Crime & Security
* ✅ Sport
* ✅ Entertainment

---

## 📊 Dashboard Access

Once running, visit:

```
http://<your-deployment-url>/dashboard
```

You’ll see a list of:

* Recent news titles
* Categories
* Source links
* Publish time

---

## 📩 WhatsApp Alerts

You’ll get real-time alerts via WhatsApp with this message:

> ✅ *New Post Published*
> 📰 Title: Punch exposes new scam
> 📂 Category: Corruption
> 🔗 [https://saamedia.info/punch-exposes-new-scam/](https://saamedia.info/punch-exposes-new-scam/)

Uses [CallMeBot WhatsApp API](https://www.callmebot.com/blog/free-api-whatsapp-messages/).

---

## 📅 Cron Job Frequency

* Every **30 minutes**
* You can modify interval in `scheduler.py`

---

## 🤝 Contributing

Pull requests are welcome. For feature requests, open an issue first to discuss changes.

---

## 🛡️ License

MIT License © 2025 [Drisa Engineering & Infotech Solutions](https://drisatech.com)

```
