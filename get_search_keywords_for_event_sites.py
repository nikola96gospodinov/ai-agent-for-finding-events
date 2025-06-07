from typing import List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from custom_typings import UserProfile
from utils import get_age_bracket

def get_search_keywords_for_event_sites(user_profile: UserProfile, model: BaseChatModel) -> List[str]:
    """
    Generate search keywords based on user profile and model.
    
    Args:
        user_profile: UserProfile object containing user information
        model: BaseChatModel instance
        
    Returns:
        List of search keywords
    """

    prompt_template = """
        You are a search query generator specialized in creating effective event discovery queries.

        IMPORTANT: Format your response ONLY as a comma-separated list of search queries with NO additional text or explanations. Limit the number of queries to 25.
        IMPORTANT: Examples (e.g.) are just for demonstration purposes. DO NOT follow them exactly. If the user has no interest in something that was provided in the examples, then do not include it in the output. The only exception is negative examples. If a negative example is provided, then under no circumstances should you include it in the output.
        
        Consider:
        - User's goals: {goals}
        - User's age bracket: {age_bracket}
        - User's interests: {interests}
        - User's occupation: {occupation}
        - User's gender: {gender}
        - Is LGBTQ+: {is_lgbtq}

        QUERY CREATION RULES:
        1. GOALS-BASED QUERIES:
        - Create personalized queries for EACH goal
        
        2. AGE-SPECIFIC QUERIES:
        - For social/community goals, ALWAYS include age bracket (e.g., "community {age_bracket}", "friends {age_bracket}") but not for professional goals (e.g., "networking {age_bracket}" or "business partner {age_bracket}" are NOT good queries) nor for more general goals (e.g., "volunteering {age_bracket}", "yoga classes {age_bracket}", "running clubs {age_bracket}" are NOT good queries)

        3. GENDER-SPECIFIC QUERIES:
        - Create one gender-specific query based on the user's gender (e.g. ladies only, men circles, etc.)

        4. LGBTQ+ query (OPTIONAL):
        - Create one LGBTQ+ query if the user is LGBTQ+ - this is optional and should only be done if the user is LGBTQ+. (e.g. "LGBTQ+ events", "LGBTQ+ community", "LGBTQ+ support group", etc.)

        5. INTEREST-BASED QUERIES:
        - Keep all interest queries to 4 words or less
        - Group related interests when logical (e.g., "tech business", "hiking outdoors")
        - DO NOT force unrelated combinations. (e.g. "fashion swimming" is NOT a good query)
        - DO NOT include age bracket in interest queries, only include it in goals-based queries

        6. PROHIBITED TERMS:
        - NO generic terms like "events", "meetups", "community", "group", "gathering", "enthusiasts", "near me" unless they are absolutely necessary
        - NO standalone "networking" or "professional networking"
        - NO generic terms like "professional connections", "find collaborators", "business collaboration", or similar terms

        7. QUERY DIVERSITY:
        - Avoid overly similar queries that would return the same results. For example, repeating the same query with different variations of the same word
        - Focus on specificity and relevance

        EXAMPLE OUTPUT FORMAT (ONLY AS A GUIDE):
        "make friends {age_bracket}, find a business partner, tech startups, python coding, hiking outdoors, AI"
        - The above are just examples. DO NOT follow them exactly. Only use them as a guide.
        
        IMPORTANT:
        Examples are just that, examples. DO NOT follow them exactly. If the user has no interest in something that was provided in the examples, then do not include it in the output. The only exception is negative examples. If a negative example is provided, then under no circumstances should you include it in the output.
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | model
    response = chain.invoke({
        "interests": user_profile["interests"],
        "goals": user_profile["goals"],
        "age_bracket": get_age_bracket(user_profile["age"]),
        "occupation": user_profile["occupation"],
        "gender": user_profile["gender"],
        "is_lgbtq": user_profile["sexual_orientation"] != "straight"
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
    keywords = [keyword.strip() for keyword in response_str.split(",")]
    return list(dict.fromkeys(keywords))
