from typing import List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from typings import UserProfile

def get_search_keywords(user_profile: UserProfile, model: BaseChatModel) -> List[str]:
    """
    Generate search keywords based on user profile and model.
    
    Args:
        user_profile: UserProfile object containing user information
        model: BaseChatModel instance
        
    Returns:
        List of search keywords
    """

    prompt_template = """
        You are a helpful assistant that generates search queries based on a user's interests and goals.
        Those search queries will be used to search for events on platforms like Eventbrite, Meetup, etc.
        The user's interests are: {interests}
        The user's goals are: {goals}

        Combination of an interest and a goal is more preferable than a single interest or goal. At the same time, don't lump together unrelated interests and goals. For example "travel dancing" or "outdoors interior design" are not good search queries.

        Limit the search queries to 3 words or less. Limit the number of search queries to 20.
        Don't include words like "events", "meetups" etc. in the search queries.
        
        The response should be a list of search queries separated by commas. For example: "tech, business, networking"
        Don't do any formatting. Just return the list of search queries as a comma separated string.
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | model
    response = chain.invoke({
        "interests": user_profile["interests"],
        "goals": user_profile["goals"]
    })

    if hasattr(response, 'content'):
        response = response.content
    
    return response.split(", ")
