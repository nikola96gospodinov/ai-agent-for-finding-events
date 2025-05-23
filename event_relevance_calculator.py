from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from typing import List, Dict
import re

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
            - Age: {age}
            - Gender: {gender}
            - Sexual Orientation: {sexual_orientation}
            - Relationship Status: {relationship_status}
            - Occupation: {occupation}
            - Interests: {interests}
            - Goals: {goals}

            SCORING SYSTEM (MAX: 90 POINTS)

            STEP 1: INTEREST MATCH (0-45 POINTS)
            Evaluate how strongly the event aligns with the user's stated interests.
            - **Perfect Match** (9-10 points): Core to the event title or primary theme
            - **Strong Match** (6-8 points): Prominently mentioned as topic/activity
            - **Moderate Match** (3-5 points): Secondary or partial focus
            - **Adjacent Match** (1-2 points): Indirect but thematically relevant
            > Total capped at 45 points

            STEP 2: GOAL ALIGNMENT (0-35 POINTS)
            Assess how well the event supports the user's goals.

            2A. **Goal Opportunity Quality** (0-20 points):
            - Exceptional opportunity: 15-20
            - Strong opportunity: 10-14
            - Moderate opportunity: 5-9
            - Weak or limited: 1-4

            2B. **Goal Efficiency** (0-15 points):
            - Multiple goals addressed well: 11-15
            - One goal clearly supported: 6-10
            - Partial/indirect support: 1-5

            STEP 3: DEMOGRAPHIC COMPATIBILITY (0-10 POINTS)
            Evaluate how well the event aligns with the user's personal attributes.
            - **Age Appropriateness** (0-4 points): How well the event suits the user's age group
            - **Relationship Status Compatibility** (0-3 points): How appropriate the event is given the user's relationship status
            - **Gender/Orientation Relevance** (0-3 points): Whether the event is inclusive of or specifically tailored to the user's gender/orientation

            DEDUCTION SYSTEM (MAX: 50 POINTS)

            STEP 1: INDUSTRY MISMATCH DEDUCTION (0-50 POINTS)
            Only apply this deduction if BOTH conditions are met:
            a. "Network professionally" or similar is one of the user's goals
            b. The event's primary purpose is networking (this is critical for this deduction to be applied)

            Important exception is that if the event aligns with a goal of the user (e.g. "find a business partner", "find a co-founder", "find a new career"), this deduction is not applied and the score is 0.
            For example, if one of the user's goals is to "find a business partner", "find a co-founder" or similar, and the event is for "entrepreneurs, business owners, and investors", this deduction is not applied even if the user is not a business owner or a investor and the score is 0 and everything else for this point is ignored.

            Evaluate the industry mismatch:
            - **Complete industry mismatch** (50 points): Event is explicitly and exclusively for professionals in a completely different field with no overlap with user's occupation
            Example: Software Engineer attending "Beauty & Wellness Industry Professionals" or "Real Estate Developers" event
            
            - **Significant industry mismatch** (30 points): Event is explicitly for professionals in a different field that has minimal overlap with user's occupation
            Example: Software Engineer attending "Legal Professionals" or "Healthcare Professionals" event
            
            - **Overly broad or undefined audience** (15 points): Event is for a very generic professional audience with no industry focus, or doesn't specify the target professional audience at all
            Example: "Networking Mixer" or "Working Professional Networking" or "Creative Professionals" with no industry specification or too broad of an audience
            
            - **No deduction** (0 points): Apply in any of these cases:
            * Event is for the user's industry or related industries
            * Event has clear overlap with the user's field, interests, and/or goals

            IMPORTANT NOTES FOR DEDUCTION SCORE:
            - This deduction uses fixed values (50, 30, 15, or 0) - there are no partial deductions between these values
            - Only apply the highest applicable deduction (do not stack them)

            IMPORTANT RULES FOR RELEVANCE SCORE:
            - Keep two scores separate: one for the relevance score and one for the deduction score.
            - Use the full range of scores for each category.
            - Each category must use at least 3 different point values (not just min/max)
            - Always justify each score with specific evidence from the event description.
            - At least one interest match is required for any score above 0.
            - Use varied phrasing and tone in your reasoning (analytical, conversational, comparative).
            - Use some variation in how you phrase judgments to avoid repetitive tone.

            RESPONSE FORMAT:
            1. Start with [X, Y] (where X is the total points after deductions and Y is the deduction score and don't include any other text. The first word are the two scores)
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
            "age": self.user_profile["age"],
            "gender": self.user_profile["gender"],
            "sexual_orientation": self.user_profile["sexual_orientation"],
            "relationship_status": self.user_profile["relationship_status"],
            "webpage_content": webpage_content
        })

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
        
        # Look for a list pattern like [X, Y]
        list_match = re.search(r'\[(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?)\]', text_to_parse)
        if list_match:
            try:
                first_num = float(list_match.group(1))
                second_num = float(list_match.group(2))

                final_score = first_num - second_num
                if final_score < 0:
                    return 0
                else:
                    return final_score
            except ValueError:
                print(f"Could not convert scores '{list_match.group(1)}' and '{list_match.group(2)}' to numbers")
                return 0
        
        print(f"Could not get the scores from '{text_to_parse}'")
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
    
    def calculate_event_relevance_score(self, webpage_content: str | None, event_details: EventDetails) -> float:
        if webpage_content is None:
            return 0

        relevance_score = self._calculate_event_relevance_based_on_interests_and_goals(webpage_content)
        price_score = self._calculate_price_score(event_details["price_of_event"], self.user_profile["budget"])
        distance_score = self._calculate_distance_score(event_details["location_of_event"])
        
        total_score = relevance_score + price_score + distance_score
        return round(total_score, 1)