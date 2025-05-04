from typings import EventDetails, UserProfile
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime

class EventDisqualifier:
    def __init__(self, user_profile: UserProfile, model: BaseChatModel):
        self.user_profile = user_profile
        self.model = model

    def check_compatibility(self, event_details: EventDetails) -> bool:
        # Check all quick conditions first
        if not self._is_event_within_acceptable_distance(event_details):
            return False
        if not self._is_event_within_acceptable_timeframe(event_details):
            return False
        if not self._is_event_within_acceptable_price_range(event_details):
            return False
        if not self._is_event_within_time_commitment(event_details):
            return False
            
        # Only check the expensive LLM operation if all other checks pass - this improves performance
        return self._is_event_suitable_for_user(event_details)

    # TODO: Function that will use Geocoding API to check if the event is in the user's threshold for distance
    def _is_event_within_acceptable_distance(self, event_details: EventDetails) -> bool:
        return True

    def _is_event_within_acceptable_timeframe(self, event_details: EventDetails) -> bool:
        timeframe_start_date = self.user_profile["timeframe"]["start_date"]
        timeframe_end_date = self.user_profile["timeframe"]["end_date"]
        
        event_date_str = event_details["date_of_event"]
        event_date = None
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
    
    def _is_event_suitable_for_user(self, event_details: EventDetails) -> bool:
        prompt_template = """
            You are a helpful assistant that determines if an event is appropriate for a user. If it is appropriate, you should return "True". If it is not, you should return "False".
            If any of the following conditions are not met, return "False" regardless of the other conditions. If an event characteristic is missing (it's None), it's not a disqualifier so move on to the next condition.

            The user is {age} years old. Do not use overly broad age ranges. For example, 28 to 49 is not acceptable. Allow some flexibility. For example, if the user is 28 or 41 but the event is for people in their 30s, it is acceptable.
            The user is {gender}. Return "False" if the event is not suitable for the user's gender.
            The user is {sexual_orientation}. Return "False" if the event is not suitable for the user's sexual orientation.
            The user is {relationship_status}. Return "False" if the event is not suitable for the user's relationship status.
            The user is {willingness_for_online} to go to online events. Return "False" if the event is online and the user is unwilling to go to online events. If an event is both online and offline, it's not a disqualifier.
            The user doesn't want to attend events {exclude_times}. All other times are fine.

            Here are the event details: {event_details}

            Your response should be "True" or "False" and then on a new line, explain your reasoning.
        """

        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.model
        response = chain.invoke({
                "event_details": event_details,
                "age": self.user_profile["age"],
                "gender": self.user_profile["gender"],
                "sexual_orientation": self.user_profile["sexual_orientation"],
                "relationship_status": self.user_profile["relationship_status"],
                "willingness_for_online": self.user_profile["willingness_for_online"],
                "exclude_times": self.user_profile["excluded_times"]
            })
        
        # Handle AIMessage if necessary
        if hasattr(response, 'content'):
            response = response.content
        
        print("Event suitability:")
        print(response)

        # Extract the first word from the response and check if it's "true"
        first_word = response.split()[0].strip().lower()
        return first_word == "true"
