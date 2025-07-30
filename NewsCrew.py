from crewai import Agent
from NewsTools import categorize_tool, summarize_tool

news_categorizer = Agent(
    role="News Categorizer",
    goal="Categorize Nigerian news articles accurately by topic",
    backstory="An expert media analyst trained in Nigerian current affairs and journalism.",
    tools=[categorize_tool]
)

news_summarizer = Agent(
    role="News Summarizer",
    goal="Write clear and engaging summaries of Nigerian news articles for publication.",
    backstory="A concise writer experienced in summarizing news content for blogs and media outlets.",
    tools=[summarize_tool]
)
