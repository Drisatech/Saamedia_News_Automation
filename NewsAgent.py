from crewai import Crew, Agent
from NewsTasks import categorize_task, summarize_task
from NewsTools import publish_to_wordpress, log_article, notify_whatsapp
from config import OPENROUTERAI_API_KEY, LLM_MODEL_NAME, TEMPERATURE

import traceback

# ✅ Use OpenRouterAI via LiteLLM
import litellm
litellm.api_key = OPENROUTERAI_API_KEY
litellm.api_base = "https://openrouter.ai/api/v1"  # required for OpenRouter

from langchain.llms import OpenAI

# Initialize the language model
llm = OpenAI(
    temperature=TEMPERATURE,
    model_name=LLM_MODEL_NAME,
    openai_api_key=OPENROUTERAI_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1"
)

# Define agents
categorizer_agent = Agent(
    role="News Categorizer",
    goal="Categorize the article into one of the 7 categories",
    backstory="Expert in classifying Nigerian news",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

summarizer_agent = Agent(
    role="News Summarizer",
    goal="Summarize news articles concisely",
    backstory="Journalist AI trained on summarization",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Create a CrewAI instance
crew = Crew(
    agents=[categorizer_agent, summarizer_agent],
    tasks=[categorize_task, summarize_task],
    verbose=True
)

# Main processing function
def process_article(title, content, link):
    try:
        result = crew.kickoff(inputs={"content": content, "title": title})

        if not isinstance(result, dict) or not result:
            print("⚠️ Agent returned empty or non-dict result:", result)
            return False, "Agent output error"

        summary = result.get("summary")
        category = result.get("category", "The Nation")

        url = publish_to_wordpress(title, summary, category)
        log_article(title, category, url, "published")
        notify_whatsapp(
            phone_number="+2348121044557",
            api_key="2254657",
            message=f"📰 New Post: {title}\nCategory: {category}\n{url}"
        )

        return True, url

    except litellm.RateLimitError as e:
        print("❌ LiteLLM rate limit hit:", str(e))
        return False, f"Rate limit hit: {str(e)}"

    except Exception as e:
        import traceback
        print("❌ General error:", str(e))
        traceback.print_exc()
        return False, f"❌ Error processing article: {str(e)}"