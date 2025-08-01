# NewsAgent.py

import os
import traceback
from crewai import Crew, Agent
from NewsTasks import get_categorize_task, get_summarize_task
from NewsTools import publish_to_wordpress, log_article, notify_whatsapp
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

# Initialize LLM
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENAI_API_KEY,
    model="mistralai/mixtral-8x7b"
)

# Define agents
categorizer_agent = Agent(
    role="News Categorizer",
    goal="Classify the article into one of the defined categories",
    backstory="Expert in Nigerian news classification",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

summarizer_agent = Agent(
    role="News Summarizer",
    goal="Provide a short summary for the article",
    backstory="Skilled in journalistic summarization",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Prepare tasks
categorize_task = get_categorize_task(categorizer_agent)
summarize_task = get_summarize_task(summarizer_agent)

# Initialize Crew
try:
    crew = Crew(
        agents=[categorizer_agent, summarizer_agent],
        tasks=[categorize_task, summarize_task],
        verbose=True,
        memory=False,
        process="sequential"
    )
except Exception as e:
    print("🚨 Crew initialization failed:", e)
    traceback.print_exc()
    raise

def process_article(title, content, link):
    try:
        result = crew.kickoff(inputs={"title": title, "content": content})

        if not isinstance(result, dict):
            return False, f"Invalid agent result format: {result}"

        summary = result.get("summary")
        category = result.get("category", CATEGORIES[0])

        if not summary:
            summary = "(No summary generated)"
        if category not in CATEGORIES:
            category = CATEGORIES[0]

        # Publish
        url = publish_to_wordpress(title, summary, category)
        # Log
        log_article(title, category, url, "published")
        # Alert
        notify_whatsapp(
            message=f"📰 New Post: {title}\nCategory: {category}\n{url}"
        )

        return True, url

    except Exception as e:
        print("❌ Error processing article:", e)
        traceback.print_exc()
        return False, f"Error processing article: {str(e)}"
