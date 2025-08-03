from crewai import Task

def get_categorize_task(agent):
    return Task(
        description=(
            "Classify the news article into an appropriate category such as "
            "'Politics', 'Business', 'Entertainment', 'Technology', 'Sports', or 'Health'.\n\n"
            "Article title: {title}\n"
            "Content:\n{content}"
        ),
        expected_output="The appropriate category label for the article.",
        agent=agent,
        output_key="category"
    )

def get_summarize_task(agent):
    return Task(
        description=(
            "Generate a concise and clear summary of the following news article. "
            "Focus on key facts and relevant context.\n\n"
            "Title: {title}\n"
            "Content:\n{content}"
        ),
        expected_output="A well-written summary paragraph (2–3 sentences) of the article.",
        agent=agent,
        output_key="summary"
    )