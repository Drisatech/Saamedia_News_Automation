# NewsTasks.py

from crewai import Task

def get_categorize_task(agent):
    return Task(
        description=(
            "Classify the news article into one of the categories: "
            "Politics, Business & Economy, Corruption, Crime & Security, "
            "Sports, Entertainment, Kogi News, Featured."
        ),
        expected_output="A single category name (string)",
        agent=agent,
        output_key="category"
    )

def get_summarize_task(agent):
    return Task(
        description="Summarize the news article in 3–5 clear sentences.",
        expected_output="A concise summary string",
        agent=agent,
        output_key="summary"
    )
