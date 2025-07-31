from crewai import Task

# Task: Categorize the article into a relevant news category
def get_categorize_task(agent):
    return Task(
        description="Classify the news article into one of the following categories: "
                    "Politics, Business & Economy, Crime & Security, Sports, Entertainment, Kogi News, Featured.",
        expected_output="A single category name best describing the article.",
        agent=agent
    )

# Task: Summarize the news article
def get_summarize_task(agent):
    return Task(
        description="Summarize the news article clearly and concisely in 3 to 5 informative sentences.",
        expected_output="A short, professional summary of the news article.",
        agent=agent
    )