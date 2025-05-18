from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime

from custom_typings import EventDetails, UserProfile, Location
from utils import calculate_distance

class EventDisqualifier:
    def __init__(self, user_profile: UserProfile, model: BaseChatModel):
        self.user_profile = user_profile
        self.model = model

    def check_compatibility(self, event_details: EventDetails) -> bool:
        # Check all quick conditions first
        if not self._is_event_sold_out(event_details):
            return False
        if not self._is_event_within_acceptable_distance(event_details):
            return False
        if not self._is_event_within_acceptable_timeframe(event_details):
            return False
        if not self._is_event_within_acceptable_price_range(event_details):
            return False
        if not self._is_event_within_time_commitment(event_details):
            return False
        if not self._is_event_within_acceptable_age_range(event_details):
            return False
        if not self._is_event_suitable_for_gender(event_details):
            return False
        if not self._is_event_suitable_for_sexual_orientation(event_details):
            return False
            
        # Only check the expensive LLM operation if all other checks pass - this improves performance
        return self._is_event_suitable_for_user(event_details)
    
    def _is_event_sold_out(self, event_details: EventDetails) -> bool:
        if event_details["is_sold_out"]:
            print("Event is sold out")
            return False
        
        return True

    def _is_event_within_acceptable_distance(self, event_details: EventDetails) -> bool:
        # If user has no location or distance threshold, distance is not a factor
        if not self.user_profile.get("location") or not self.user_profile.get("distance_threshold"):
            return True
            
        event_location = event_details["location_of_event"]
        if not event_location.get("latitude") or not event_location.get("longitude"):
            # If event has no coordinates, we can't calculate distance
            return True
        
        latitude = event_location.get("latitude")
        longitude = event_location.get("longitude")
        assert latitude is not None and longitude is not None
            
        event_coordinates: Location = {
            "latitude": latitude,
            "longitude": longitude
        }
        distance = calculate_distance(loc1=self.user_profile["location"], loc2=event_coordinates, distance_unit=self.user_profile["distance_threshold"]["unit"])
            
        # Check if the event is within the user's acceptable distance
        max_distance = self.user_profile["distance_threshold"]["distance_threshold"]
        within_threshold = distance <= max_distance
        
        if not within_threshold:
            print("Event is too far")
            return False
            
        return within_threshold

    def _is_event_within_acceptable_timeframe(self, event_details: EventDetails) -> bool:
        timeframe_start_date = self.user_profile["timeframe"]["start_date"]
        timeframe_end_date = self.user_profile["timeframe"]["end_date"]
        
        event_date_str = event_details["date_of_event"]
        event_date: datetime
        if event_date_str:
            event_date = datetime.strptime(event_date_str, "%d-%m-%Y")
        
        if timeframe_start_date and event_date < timeframe_start_date:
            print("Event is before the timeframe start date")
            return False
        if timeframe_end_date and event_date > timeframe_end_date:
            print("Event is after the timeframe end date")
            return False

        return True

    def _is_event_within_acceptable_price_range(self, event_details: EventDetails) -> bool:
        if event_details["price_of_event"] and not self.user_profile["willingness_to_pay"]:
            print("Event is paid and the user doesn't want to pay")
            return False
        
        if event_details["price_of_event"] and self.user_profile["willingness_to_pay"]:
            if event_details["price_of_event"] > self.user_profile["budget"]:
                print("Event is paid and the price is higher than the user's budget")
                return False

        return True
    
    def _is_event_within_time_commitment(self, event_details: EventDetails) -> bool:
        if event_details["start_time"] and event_details["end_time"] and self.user_profile["time_commitment_in_minutes"]:
            start_time = datetime.strptime(event_details["start_time"], "%H:%M")
            end_time = datetime.strptime(event_details["end_time"], "%H:%M")
            time_difference = end_time - start_time
            if time_difference.total_seconds() > self.user_profile["time_commitment_in_minutes"] * 60:
                print("Event is longer than the user's acceptable time commitment")
                return False

        return True
    
    def _is_event_within_acceptable_age_range(self, event_details: EventDetails) -> bool:
        AGE_MARGIN = 2  # 2-year margin of tolerance
        
        if event_details["age_range"]:
            if event_details["age_range"]["min_age"]:
                if event_details["age_range"]["min_age"] > self.user_profile["age"] + AGE_MARGIN:
                    print("Event is outside the user's acceptable age range")
                    return False
            if event_details["age_range"]["max_age"]:
                if event_details["age_range"]["max_age"] < self.user_profile["age"] - AGE_MARGIN:
                    print("Event is outside the user's acceptable age range")
                    return False

        return True
    
    def _is_event_suitable_for_gender(self, event_details: EventDetails) -> bool:
        if event_details["gender_bias"] and self.user_profile["gender"]:
            if self.user_profile["gender"] not in event_details["gender_bias"]:
                print("Event is not suitable for the user's gender")
                return False

        return True
    
    def _is_event_suitable_for_sexual_orientation(self, event_details: EventDetails) -> bool:
        if event_details["sexual_orientation_bias"] and self.user_profile["sexual_orientation"]:
            if self.user_profile["sexual_orientation"] not in event_details["sexual_orientation_bias"]:
                print("Event is not suitable for the user's sexual orientation")
                return False

        return True

    def _is_event_suitable_for_user(self, event_details: EventDetails) -> bool:
        prompt_template = """
            You are a helpful assistant that determines if an event is appropriate for a user. Your goal is to be inclusive and only disqualify events that are explicitly unsuitable for the user.

            Here are the event details: {event_details}

            Consider the following rules:
            1. If an event characteristic is missing (None), assume it's suitable for everyone
            2. Only return "False" if there is a clear mismatch between the event requirements and user characteristics
            3. When in doubt, return "True" to give the user more options

            Check these specific conditions:
            - Relationship Status: The user is {relationship_status}. Only return "False" if the event explicitly requires a different status
            - Online Events: The user is {willingness_for_online} to attend online events. Only return "False" if the event is online-only and user is unwilling or vice versa
            - Time Restrictions: The user doesn't want to attend events {exclude_times}. Only return "False" if the event time matches these excluded times

            Your response should be "True" or "False" and then on a new line, explain your reasoning.
        """

        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.model
        response = chain.invoke({
                "event_details": event_details,
                "relationship_status": self.user_profile["relationship_status"],
                "willingness_for_online": "willing" if self.user_profile["willingness_for_online"] == True else "unwilling",
                "exclude_times": self.user_profile["excluded_times"]
            })
        
        # Handle AIMessage if necessary
        if hasattr(response, 'content'):
            response = response.content
        
        print("Event suitability:")
        print(response)

        try:
            first_word = str(response).split()[0].strip().lower()
        except (AttributeError, IndexError):
            print("Warning: Could not parse response, defaulting to False")
            return False

        return first_word == "true"