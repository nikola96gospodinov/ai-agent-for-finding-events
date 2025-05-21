from typing import List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from custom_typings import UserProfile

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

        Consider:
        - User's goals: {goals} - These are HIGHEST priority
        - User's age bracket: {age}s (e.g., 20s, 30s, 40s)
        - User's interests: {interests}

        QUERY CREATION RULES:
        1. GOALS-BASED QUERIES (HIGHEST PRIORITY):
        - Create personalized queries for EACH goal
        - Include age bracket for social goals (e.g., "make friends 20s", "dating 30s") but not for professional goals (e.g., "tech networking 30s" or "startup partner 20s" are not good queries)

        2. AGE-SPECIFIC QUERIES:
        - For social/community goals, ALWAYS include age bracket (e.g., "community 30s", "friends 20s") but not for professional goals (e.g., "networking 30s" or "business partner 20s" are not good queries)
        - DO NOT include age for hobby/interest queries. This is crucial.

        3. INTEREST-BASED QUERIES:
        - Keep all interest queries to 4 words or less
        - Group related interests when logical (e.g., "tech business", "hiking outdoors")
        - DO NOT force unrelated combinations

        4. PROHIBITED TERMS:
        - NO generic terms like "events", "meetups", "community", "group", "gathering", "enthusiasts" unless they are absolutely necessary
        - NO standalone "networking" or "professional networking"
        - NO generic terms like "professional connections", "find collaborators", "business collaboration" or similar terms

        5. QUERY DIVERSITY:
        - Avoid overly similar queries that would return the same results. For example, repeating the same query with different variations of the same word
        - Focus on specificity and relevance

        EXAMPLE OUTPUT FORMAT:
        make friends 20s, find a business partner, tech startups, python coding, hiking outdoors, AI
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
    keywords = [keyword.strip() for keyword in response_str.split(",")]
    return list(dict.fromkeys(keywords))
