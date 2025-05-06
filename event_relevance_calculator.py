from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from custom_typings import UserProfile

def calculate_event_relevance(webpage_content: str, user_profile: UserProfile, model: BaseChatModel) -> float | int:
    template = """
        You are a helpful personal assistant who evaluates events for relevance to a given user.

        Your task is to scan the event information and determine how relevant it is to the user using a precise scoring system.

        THE WEB PAGE CONTENT:
        {webpage_content}

        USER INFORMATION:
        - Occupation: {occupation}
        - Interests: {interests}
        - Goals: {goals}

        SCORING SYSTEM (TOTAL: 0-100):

        STEP 1: INTEREST MATCH (0-45 POINTS)
        - Primary interest match evaluation (0-30 points):
        * Perfect match (central topic of event): 10 points per match
        * Strong match (explicitly mentioned): 7 points per match
        * Moderate match (component of event): 4 points per match
        * No limit on number of matches, but maximum total: 30 points

        - Interest depth assessment (0-15 points):
        * Beginner-friendly for new interests: 3-5 points
        * Intermediate level for developing interests: 6-10 points
        * Advanced/specialized for deep interests: 11-15 points

        STEP 2: GOAL ALIGNMENT (0-35 POINTS)
        - Goal opportunity quality (0-20 points):
        * Exceptional opportunity for goal: 15-20 points
        * Good opportunity for goal: 10-14 points
        * Basic opportunity for goal: 5-9 points
        * Limited opportunity for goal: 1-4 points

        - Goal efficiency (0-15 points):
        * Multiple goals addressed simultaneously: 10-15 points
        * Single goal addressed effectively: 5-9 points
        * Partial goal support: 1-4 points

        STEP 3: EVENT QUALITY FACTORS (0-20 POINTS)
        - Exclusivity/rarity (0-5 points)
        - Timing convenience (0-5 points)
        - Professional development value (0-5 points)
        - Networking potential quality (0-5 points)

        IMPORTANT RULES:
        - Use the FULL range of points within each category
        - Be precise in your scoring - use specific point values, not just the maximum
        - There must be at least one interest match for a score above 0
        - Calculate exact point values for each category and subcategory
        - Justify each point allocation with specific evidence from the event description

        RESPONSE FORMAT:
        1. Start with "X" (where X is the total points and don't include any other text. The first word is the score)
        2. Provide a 1-2 sentence summary of relevance
        3. Show detailed scoring breakdown with sub-scores for each component
        4. Conclude with specific reasons why this event ranks where it does relative to an average relevant event
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    # Include the webpage content in the prompt
    result = chain.invoke({
        "occupation": user_profile["occupation"],
        "interests": user_profile["interests"],
        "goals": user_profile["goals"],
        "webpage_content": webpage_content
    })

    # Handle AIMessage if necessary
    if hasattr(result, 'content'):
        result = result.content

    print(f"Event relevance score: {result}")

    score_text = "0"
    for word in result.split():
        cleaned_word = ''.join(c for c in word if c.isdigit() or c == '.')
        if cleaned_word and cleaned_word[0].isdigit():
            if cleaned_word.count('.') <= 1:
                score_text = cleaned_word
                break
    try:
        return int(score_text)
    except ValueError:
        try:
            return float(score_text)
        except ValueError:
            print(f"Could not convert score '{score_text}' to a number")
            return 0