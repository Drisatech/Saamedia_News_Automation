
from crewai import Task
from NewsCrew import news_categorizer, news_summarizer 

categorize_task = Task(
    description="Given a news article, classify it into one of these categories: 'The Nation', 'Politics', 'Business & Economy', 'Corruption', 'Crime & Security', 'Sports', 'Entertainment', 'Kogi News', 'Featured'",
    expected_output="The correct category name only.",
    agent=news_categorizer,
    output_key="category"
)

summarize_task = Task(
    description="Summarize the provided news article into a short, engaging summary for blog publication. Avoid redundancy.",
    expected_output="1-2 paragraph readable summary.",
    agent=news_summarizer,
    output_key="summary"
)
