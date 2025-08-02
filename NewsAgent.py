
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
def process_article(title, content, link):
    try:
        # Replace this with your actual processing logic
        print(f"Processing article: {title}")
        
        # Do something with content or link...

        return True, "Successfully processed"

    except Exception as e:
        return False, f"Error: {str(e)}"
