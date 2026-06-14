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
