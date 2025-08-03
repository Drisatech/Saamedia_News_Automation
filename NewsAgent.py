# NewsAgent.py

import os
import traceback
import requests
from NewsTasks import get_categorize_task, get_summarize_task
from NewsTools import log_article, notify_whatsapp
from config import OPENAI_API_KEY
from dotenv import load_dotenv
from crewai import Crew, Agent, Task
from litellm import completion

# Configuration
MODEL = "openrouter/openai/gpt-3.5-turbo"  # or any OpenRouter-compatible model

def generate_response(prompt):
    try:
        response = completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Agents
categorizer_agent = Agent(
    role="News Categorizer",
    goal="Classify news articles into categories like Politics, Sports, Business, etc.",
    backstory="An expert journalist with decades of experience in news classification.",
    tools=[],
    verbose=True
)

summarizer_agent = Agent(
    role="News Summarizer",
    goal="Generate short summaries of news articles.",
    backstory="A seasoned writer known for condensing complex stories into quick reads.",
    tools=[],
    verbose=True
)

# POST TO WORDPRESS FUNCTION
def post_to_wordpress(title, content, category, image_url=None):
    try:
        post_payload = {
            "title": title,
            "content": content,
            "category": category,
            "image_url": image_url
        }

        response = requests.post(
            "https://saamedia.info/wp-json/saamedia/v1/post-news",
            json=post_payload,
            timeout=10
        )

        if response.status_code == 200:
            return True, f"Posted successfully. WP Response: {response.json()}"
        else:
            return False, f"WordPress API Error: {response.text}"

    except Exception as e:
        return False, f"Exception in post_to_wordpress: {str(e)}"

# MAIN ARTICLE PROCESSOR
def process_article(title, content, link, category=None, image_url=None):
    try:
        print(f"Processing article: {title}")

        # Step 1: Post to WordPress
        success, message = post_to_wordpress(title, content, category or "Uncategorized", image_url)

        # Step 2: Logging or notification
        if success:
            log_article(title, link, status="published", DateTime=None)
            notify_whatsapp(f"✅ Posted: {title}")
        else:
            notify_whatsapp(f"❌ Failed: {title} | {message}")

        return success, message

    except Exception as e:
        return False, f"Unexpected error: {str(e)}"