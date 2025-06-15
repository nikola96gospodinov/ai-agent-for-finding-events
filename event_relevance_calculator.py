from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from typing import List, Dict
import re
import ast

from custom_typings import UserProfile, Location, EventDetails, industry_mismatch_options, ScoringSystem
from utils import calculate_distance, retry_with_backoff

class EventRelevanceCalculator:
    def __init__(self, model: BaseChatModel, user_profile: UserProfile):
        self.model = model
        self.user_profile = user_profile

    def _industry_mismatch_deduction(self, industry_mismatch: industry_mismatch_options) -> float:
        if industry_mismatch == "complete_mismatch":
            return 50
        elif industry_mismatch == "significant_mismatch":
            return 35
        elif industry_mismatch == "overly_broad_mismatch":
            return 25
        return 0

    def _calculate_event_relevance_based_on_interests_and_goals(self, webpage_content: str) -> float | int:
        template = """
            You are a helpful personal assistant who evaluates events for relevance to a given user.

            Your task is to scan the event information and determine how relevant it is to the user using a precise scoring system and rich reasoning.

            THE WEB PAGE CONTENT:
            {webpage_content}

            STEP 1: INTEREST MATCH
            Count how many interests the event matches with the user's interests using the provided tiers.
            Interests are: {interests}
            - **Exact Match**: Core to the event title or primary theme
            - **Partial Match**: Mentioned as topic/activity but not the core theme
            - **Weak Match**: Indirect but thematically relevant
            > Only use the the provided tires to categorize matches.

            STEP 2: GOAL FULFILLMENT MATCH
            Count how many goals the event matches with the user's goals using the provided tiers.
            Goals are: {goals}
            - **Exact Match**: The event is explicitly designed to help the user achieve one of their goals
            - **Partial Match**: The event is indirectly related to the user's goal
            - **Weak Match**: The event is only tangentially related to the user's goal
            > Only use the the provided tires to categorize matches.

            DEDUCTION SYSTEM

            STEP 1: INDUSTRY MISMATCH DEDUCTION
            IMPORTANT: Only apply this deduction if the event's primary purpose is professional networking and the event is not for the user's industry or tightly related industries.
            User's occupation is {occupation}

            Important exception is that if the event aligns with a goal of the user (e.g. "find a business partner", "find a co-founder", "find a new career"), this deduction is not applied and the score is 0.
            For example, if one of the user's goals is to "find a business partner", "find a co-founder" or similar, and the event is for "entrepreneurs, business owners, and investors", this deduction is not applied even if the user is not a business owner or a investor and the score is 0 and everything else for this point is ignored.

            Evaluate the industry mismatch against the user's occupation:
            - **Complete industry mismatch**: Event is explicitly and exclusively for professionals in a completely different field with no overlap with user's occupation
                Example: Software Engineer attending "Beauty & Wellness Industry Professionals" or "Real Estate Developers" event
            - **Significant industry mismatch**: Event is explicitly for professionals in a different field that has some overlap with user's occupation
                Example: Software Engineer attending "UI Design Professionals" or "Copywriting Professionals" event
            - **Overly broad or undefined audience**: Event is for a very generic professional audience with no industry focus, or doesn't specify the target professional audience at all
                Example: "Networking Mixer" or "Working Professional Networking" or "Creative Professionals" with no industry specification or too broad of an audience.
            - **No deduction**: Apply in any of these cases:
                * Event is for the user's industry or tightly related industries
                * Event has clear overlap with the user's field, interests, and/or goals

            IMPORTANT NOTES FOR DEDUCTION SCORE:
            - Only use the the provided tires to categorize mismatches.

            IMPORTANT RULES FOR RELEVANCE SCORE:
            - Never exceed the maximum score for each category.
            - Keep two scores separate: one for the relevance score and one for the deduction score.
            - Always justify each score with specific evidence from the event description.
            - At least one interest match is required for any score above 0.
            - Use varied phrasing and tone in your reasoning (analytical, conversational, comparative).
            - Use some variation in how you phrase judgments to avoid repetitive tone.

            RESPONSE FORMAT:
            1. Start with a Python dictionary with the following format:
            - interests:
                - exact_match: number of interests that are an exact match
                - partial_match: number of interests that are a partial match
                - weak_match: number of interests that are a weak match
            - goals:
                - exact_match: number of goals that are an exact match
                - partial_match: number of goals that are a partial match
                - weak_match: number of goals that are a weak match
            - industry_mismatch: one of the following options: {industry_mismatch_options}
            Example:
            {{
                "interests": {{
                    "exact_match": 1,
                    "partial_match": 2,
                    "weak_match": 5
                }},
                "goals": {{
                    "exact_match": 1,
                    "partial_match": 0,
                    "weak_match": 3
                }},
                "industry_mismatch": "complete_mismatch"
            }}
            Don't do any formatting. Just return the Python dictionary as plain text. Under any circumstances, don't use ```python or ``` in the response.
            Under any circumstances, don't return JSON and make sure the response is a valid Python dictionary. This is crucial.
            2. Provide a 1-2 sentence summary of relevance
            3. Show detailed scoring breakdown with sub-scores for each component
            4. Conclude with specific reasons why this event ranks where it does relative to an average relevant event
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.model

        try:
            result = retry_with_backoff(
                chain.invoke,
                max_retries=5,
                base_delay=2.0,
                input={
                    "occupation": self.user_profile["occupation"],
                    "interests": self.user_profile["interests"],
                    "goals": self.user_profile["goals"],
                    "webpage_content": webpage_content,
                    "industry_mismatch_options": industry_mismatch_options
                }
            )

            if hasattr(result, 'content'):
                result = result.content

            print(f"Event relevance score: {result}")

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
            
            # Look for a dictionary pattern like
            dict_pattern = r'\{.*\}'
            dict_match = re.search(dict_pattern, text_to_parse, re.DOTALL)
            if dict_match:
                text_to_parse = dict_match.group(0)

            try:
                scoring_system: ScoringSystem = ast.literal_eval(text_to_parse)
                interests_score = min(scoring_system["interests"]["exact_match"] * 20 + scoring_system["interests"]["partial_match"] * 10 + scoring_system["interests"]["weak_match"] * 2, 50)
                goals_score = min(scoring_system["goals"]["exact_match"] * 20 + scoring_system["goals"]["partial_match"] * 10 + scoring_system["goals"]["weak_match"] * 2, 30)
                industry_mismatch_score = self._industry_mismatch_deduction(scoring_system["industry_mismatch"])

                return interests_score + goals_score - industry_mismatch_score
            except (SyntaxError, ValueError) as e:
                print(f"Error parsing scoring system: {e}")
                return 0

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return 0
            
    def _calculate_price_score(self, price_of_event: int | float | None, budget: int | float) -> float:        
        if price_of_event is None:
            return 0
        elif price_of_event > budget:
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
    
    def _calculate_demographic_score(self, event_details: EventDetails) -> float:
        score = 0

        if event_details["age_range"] and self.user_profile["age"]:
            # +18 exception
            if self.user_profile["age"] >= 18 and event_details["age_range"]["min_age"] == 18 and not event_details["age_range"]["max_age"]:
                score += 1
            else:
                score += 4

        if event_details["gender_bias"] and self.user_profile["gender"]:
            if len(event_details["gender_bias"]) == 1:
                score += 3
            else:
                score += 1

        if event_details["relationship_status_bias"] and self.user_profile["relationship_status"]:
            if len(event_details["relationship_status_bias"]) == 1:
                score += 3
            else:
                score += 1

        if event_details["sexual_orientation_bias"] and self.user_profile["sexual_orientation"]:
            if len(event_details["sexual_orientation_bias"]) == 1:
                score += 3
            else:
                score += 1
        
        return min(score, 10)

    def calculate_event_relevance_score(self, webpage_content: str | None, event_details: EventDetails) -> float:
        if webpage_content is None:
            return 0

        relevance_score = self._calculate_event_relevance_based_on_interests_and_goals(webpage_content)
        price_score = self._calculate_price_score(event_details["price_of_event"], self.user_profile["budget"])
        distance_score = self._calculate_distance_score(event_details["location_of_event"])
        demographic_score = self._calculate_demographic_score(event_details)
        
        total_score = relevance_score + price_score + distance_score + demographic_score
        return round(total_score, 1)