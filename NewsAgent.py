from crewai import Crew, Agent
from langchain_community.chat_models import ChatOpenRouter
from NewsTasks import categorize_task, summarize_task
from NewsTools import publish_to_wordpress, log_article, notify_whatsapp
from config import OPENROUTERAI_API_KEY, LLM_MODEL_NAME, TEMPERATURE, CATEGORIES

import traceback

# ✅ Initialize OpenRouterAI model
llm = ChatOpenRouter(
    api_key=OPENROUTERAI_API_KEY,
    model=LLM_MODEL_NAME,
    temperature=TEMPERATURE
)

# ✅ Define agents
categorizer_agent = Agent(
    role="News Categorizer",
    goal="Categorize the article into one of the news categories",
    backstory="Expert in classifying Nigerian news based on content and keywords.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

summarizer_agent = Agent(
    role="News Summarizer",
    goal="Summarize Nigerian news articles concisely and factually.",
    backstory="A journalist AI trained on summarization and editorial writing.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# ✅ CrewAI pipeline
crew = Crew(
    agents=[categorizer_agent, summarizer_agent],
    tasks=[categorize_task, summarize_task],
    verbose=True
)

# ✅ Main processing function
def process_article(title, content, link):
    try:
        result = crew.kickoff(inputs={"content": content, "title": title})

        if not isinstance(result, dict) or not result:
            return False, "Agent returned no or invalid output"

        summary = result.get("summary") or "No summary generated."
        category = result.get("category", "The Nation")

        # Sanity check: default to first category if invalid
        if category not in CATEGORIES:
            category = CATEGORIES[0]

        # ✅ Step 1: Publish to WordPress
        url = publish_to_wordpress(title, summary, category)

        # ✅ Step 2: Log article
        log_article(title, category, url, "published")

        # ✅ Step 3: WhatsApp notification
        notify_whatsapp(
            phone_number="+2348121044557",
            api_key="2254657",  # Optional: Move to config if reused
            message=f"📰 New Post: {title}\nCategory: {category}\n{url}"
        )

        return True, url

    except Exception as e:
        print("❌ Error in process_article:", str(e))
        traceback.print_exc()
        return False, f"Error processing article: {str(e)}"