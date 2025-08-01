
import os
import traceback
from NewsTasks import get_categorize_task, get_summarize_task
from NewsTools import publish_to_wordpress, log_article, notify_whatsapp
from config import OPENAI_API_KEY
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crewai import Crew, Agent, Task
from litellm import completion

# Configuration
MODEL = "openrouter/openai/gpt-3.5-turbo"  # or whichever OpenRouter-compatible model you prefer

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

# Main Article Processor
def process_article(title, text, url):
    try:
        print(f"\n🔍 Processing: {title}")
        print("📂 Sending to categorizer_agent...")
        category_prompt = f"Classify the following news headline:\n\nTitle: {title}\n\nText: {text}\n\nCategory:"
        category = generate_response(category_prompt).strip()

        print("📂 Sending to summarizer_agent...")
        summary_prompt = f"Summarize the following article:\n\nTitle: {title}\n\nText: {text}\n\nSummary:"
        summary = generate_response(summary_prompt).strip()

        return {
            "title": title,
            "text": text,
            "summary": summary,
            "category": category,
            "url": url
        }
    except Exception as e:
        print(f"❌ Error processing article: {e}")
        return None
