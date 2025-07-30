
from crewai import Crew
from langchain_openai import ChatOpenAI
from NewsTasks import categorize_task, summarize_task
from crewai import Agent
from NewsTools import publish_to_wordpress, log_article, notify_whatsapp

# CrewAI Agents
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

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

# Crew Setup
crew = Crew(
    agents=[categorizer_agent, summarizer_agent],
    tasks=[categorize_task, summarize_task],
    verbose=True
)

def process_article(title, content, link):
    result = crew.kickoff(inputs={"content": content, "title": title})

    if not result or not isinstance(result, dict):
        return False, "Invalid agent result"

    summary = result.get("summary")
    category = result.get("category", "The Nation")

    # Publish to WordPress
    url = publish_to_wordpress(title, summary, category)

    # Log to SQLite
    log_article(title, category, url, "published")

    # WhatsApp alert
    notify_whatsapp(
        phone_number="+2348121044557",  # Replace with your number
        api_key="2254657",  # Replace with your key
        message=f" New Post: {title}\nCategory: {category}\n{url}"
    )

    return True, url
