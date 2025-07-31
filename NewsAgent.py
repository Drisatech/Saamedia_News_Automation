from crewai import Crew, Agent
from langchain_openai import ChatOpenAI
from NewsTasks import categorize_task, summarize_task
from NewsTools import publish_to_wordpress, log_article, notify_whatsapp

# Initialize the language model
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

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
    """Process article through categorization, summarization, and publishing pipeline."""
    try:
        result = crew.kickoff(inputs={"content": content, "title": title})

        if not isinstance(result, dict) or not result:
            return False, "Agent returned invalid output"

        summary = result.get("summary")
        category = result.get("category", "The Nation")

        # Step 1: Publish to WordPress
        url = publish_to_wordpress(title, summary, category)

        # Step 2: Log article
        log_article(title, category, url, "published")

        # Step 3: WhatsApp alert
        notify_whatsapp(
            phone_number="+2348121044557",
            api_key="2254657",  # Ideally loaded from environment
            message=f"📰 New Post: {title}\nCategory: {category}\n{url}"
        )

        return True, url

    except Exception as e:
        return False, str(e)