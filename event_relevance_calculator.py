from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from typings import UserProfile

def calculate_event_relevance(webpage_content: str, user_profile: UserProfile, model: BaseChatModel) -> float:
    template = """
        You are a helpful personal assistant who evaluates events for relevance to a given user.

        Your task is to scan the event information and determine how relevant it is to the user. Follow this EXACT scoring system and provide your analysis in the required format.

        THE WEB PAGE CONTENT:
        {webpage_content}

        USER INFORMATION:
        - Occupation: {occupation} (This provides context but is not usually a primary factor)
        - Interests: {interests}
        - Goals: {goals}

        SCORING SYSTEM (TOTAL: 0-100):

        STEP 1: INTEREST MATCH (0-50 POINTS)
        - Direct match with primary interests: 15 points per match (maximum 30 points)
        - Related/adjacent interests: 7 points per match (maximum 14 points)
        - Event theme general alignment with interest areas: 0-6 points

        STEP 2: GOAL ALIGNMENT (0-40 POINTS)
        - Direct opportunity for stated goal: 15 points per goal (maximum 30 points)
        - Indirect but meaningful support for goals: 5-10 points per goal
        - Event format supports goal achievement: 0-10 points

        STEP 3: CONTEXTUAL RELEVANCE (0-10 POINTS)
        - Professional relevance (alignment with occupation): 0-5 points
        - Special factors (unique opportunities, rare events): 0-5 points

        IMPORTANT RULES:
        - There MUST be at least one clear interest match for a score above 0
        - Ignore very loose or tenuous connections
        - Calculate exact point values for each category
        - Sum all points for the final score

        RESPONSE FORMAT:
        1. Start with "RELEVANCE SCORE: X%" (where X is the total points)
        2. Provide a 1-2 sentence summary of relevance
        3. Show detailed scoring breakdown:
        - Interest Match: X/50 points
            * List specific matched interests and points awarded
        - Goal Alignment: X/40 points
            * Explain how event supports each relevant goal
        - Contextual Relevance: X/10 points
            * Explain any professional/special relevance
        4. Conclude with overall assessment of why user should or should not consider this event

        Score interpretation:
        - 80-100: Highly relevant
        - 60-79: Very relevant
        - 40-59: Moderately relevant
        - 20-39: Somewhat relevant
        - 0-19: Minimally relevant
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

    return result