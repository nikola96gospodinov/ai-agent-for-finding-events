from typing import List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from custom_typings import UserProfile

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
        The user's age is: {age}. For example, if the user is 30, the age should be "30s". If the user is 25, the age should be "20s" etc.

        Start with the user's goals and provide a search query for each goal. 
        Certain goals might benefit from including the user's age in the search queries. For example, "30s make new friends" and "40s dating" are good search queries. At the same time, "20s business networking" or "tech 40s" are not good search queries as those goals are not relevant to the user's age.
        
        Then move on to the user's interests.
        Some interests might be related to each other. For example, "tech" and "business" are related. "outdoors" and "hiking" are related. Make sure to combine interests that are related but don't force it.

        Limit the search queries to 4 words or less. The number of search queries should be between 5 and 20.
        Don't include words like "events", "meetups" etc. in the search queries. Only include words like "networking" if they are extremely relevant to the rest of the search query but do not use excessively and don't use on its own.
        Avoid having overly similar search queries that will potentially return the same events.
        
        The response should be a list of search queries separated by commas. For example: "tech, business, networking"
        Don't do any formatting. Just return the list of search queries as a comma separated string.
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | model
    response = chain.invoke({
        "interests": user_profile["interests"],
        "goals": user_profile["goals"],
        "age": user_profile["age"]
    })

    if hasattr(response, 'content'):
        response = response.content
    elif isinstance(response, str):
        response = response
    elif isinstance(response, list):
        response = ", ".join(str(item) for item in response)
    else:
        response = str(response)
    
    response_str = str(response)
    return [keyword.strip() for keyword in response_str.split(",")]
