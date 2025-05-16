from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from typing import List, Dict

from custom_typings import UserProfile, Location, EventDetails
from utils import calculate_distance

class EventRelevanceCalculator:
    def __init__(self, model: BaseChatModel, user_profile: UserProfile):
        self.model = model
        self.user_profile = user_profile

    def _calculate_event_relevance_based_on_interests_and_goals(self, webpage_content: str) -> float | int:

        template = """
            You are a helpful personal assistant who evaluates events for relevance to a given user.

            Your task is to scan the event information and determine how relevant it is to the user using a precise scoring system and rich reasoning.

            THE WEB PAGE CONTENT:
            {webpage_content}

            USER INFORMATION:
            - Occupation: {occupation}
            - Interests: {interests}
            - Goals: {goals}

            SCORING SYSTEM (MAX: 90 POINTS)

            STEP 1: INTEREST MATCH (0-40 POINTS)
            Evaluate how strongly the event aligns with the user's stated interests.
            - **Perfect Match** (9-10 points): Core to the event title or primary theme
            - **Strong Match** (6-8 points): Prominently mentioned as topic/activity
            - **Moderate Match** (3-5 points): Secondary or partial focus
            - **Adjacent Match** (1-2 points): Indirect but thematically relevant
            > Total capped at 40 points

            STEP 2: GOAL ALIGNMENT (0-30 POINTS)
            Assess how well the event supports the user's goals.

            2A. **Goal Opportunity Quality** (0-20 points):
            - Exceptional opportunity: 17-20
            - Strong opportunity: 13-16
            - Moderate opportunity: 7-12
            - Weak or limited: 1-6

            2B. **Goal Efficiency** (0-10 points):
            - Multiple goals addressed well: 8-10
            - One goal clearly supported: 5-7
            - Partial/indirect support: 1-4

            STEP 3: EVENT QUALITY FACTORS (0-20 POINTS)
            Evaluate how well the event fits the user's preferences and schedule.
            - **Exclusivity or Rarity** (0-5 points)
            - **Timing Convenience** (0-5 points)
            - **Professional Development Value** (0-5 points)
            - **Networking Potential** (0-5 points)

            IMPORTANT RULES:
            - Use the full range of scores for each category.
            - Each category must use at least 3 different point values (not just min/max)
            - Always justify each score with specific evidence from the event description.
            - At least one interest match is required for any score above 0.
            - Use varied phrasing and tone in your reasoning (analytical, conversational, comparative).
            - Use some variation in how you phrase judgments to avoid repetitive tone.

            RESPONSE FORMAT:
            1. Start with "X" (where X is the total points and don't include any other text. The first word is the score)
            2. Provide a 1-2 sentence summary of relevance
            3. Show detailed scoring breakdown with sub-scores for each component
            4. Conclude with specific reasons why this event ranks where it does relative to an average relevant event
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.model

        # Include the webpage content in the prompt
        result = chain.invoke({
            "occupation": self.user_profile["occupation"],
            "interests": self.user_profile["interests"],
            "goals": self.user_profile["goals"],
            "webpage_content": webpage_content
        })

        if hasattr(result, 'content'):
            result = result.content

        print(f"Event relevance score: {result}")

        score_text = "0"
        # Handle different possible result types
        if isinstance(result, str):
            text_to_parse = result
        elif isinstance(result, BaseMessage):
            text_to_parse = result.content
        elif isinstance(result, (List, Dict)):
            text_to_parse = str(result)
        else:
            print(f"Unexpected result type: {type(result)}")
            return 0

        # Convert to string to ensure we can split
        text_to_parse = str(text_to_parse)
        for word in text_to_parse.split():
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
            
    def _calculate_price_score(self, price_of_event: int | float, budget: int | float) -> float:
        if price_of_event > budget:
            return 0
        elif price_of_event == 0:
            return 5
        else:
            price_ratio = 1 - (price_of_event / budget)
            return 5 * price_ratio
        
    def _calculate_distance_score(self, location_of_event: Location) -> float:
        if not self.user_profile["location"] or not self.user_profile["distance_threshold"]:
            return 0
        
        if not location_of_event or not location_of_event.get("latitude") or not location_of_event.get("longitude"):
            return 0
        
        latitude = location_of_event.get("latitude")
        longitude = location_of_event.get("longitude")
        assert latitude is not None and longitude is not None
        
        event_coordinates: Location = {
            "latitude": float(latitude),
            "longitude": float(longitude)
        }
        
        distance = calculate_distance(self.user_profile["location"], event_coordinates, self.user_profile["distance_threshold"]["unit"])

        distance_ratio = 1 - (distance / self.user_profile["distance_threshold"]["distance_threshold"])
        return 5 * max(0, distance_ratio)
    
    def calculate_event_relevance_score(self, webpage_content: str | None, event_details: EventDetails) -> float:
        if webpage_content is None:
            return 0

        relevance_score = self._calculate_event_relevance_based_on_interests_and_goals(webpage_content)
        price_score = self._calculate_price_score(event_details["price_of_event"], self.user_profile["budget"])
        distance_score = self._calculate_distance_score(event_details["location_of_event"])
        
        total_score = relevance_score + price_score + distance_score
        return round(total_score, 1)