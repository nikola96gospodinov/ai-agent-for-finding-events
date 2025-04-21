from typings import EventDetails, UserProfile
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime

class EventDisqualifier:
    def __init__(self, event_details: EventDetails, user_profile: UserProfile, model: OllamaLLM):
        self.event_details = event_details
        self.user_profile = user_profile
        self.model = model

    def _check_compatibility(self, event_restrictions, user_characteristics) -> bool:
        prompt_template = """
            You are a helpful assistant that determines if an event is disqualifying for a user. If it is, you should return "True". If it is not, you should return "False".

            The event has the following restriction:
            {event_restrictions}

            The user has the following characteristic:
            {user_characteristics}
        """

        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.model
        response = chain.invoke({"event_restrictions": event_restrictions, "user_characteristics": user_characteristics})
        return response.strip().lower() == "true"

    # TODO: Function that will use Geocoding API to check if the event is in the user's threshold for distance
    def _is_event_within_acceptable_distance(self) -> bool:
        return True

    def _is_event_within_acceptable_timeframe(self) -> bool:
        timeframe_start_date = self.user_profile["timeframe"]["start_date"]
        timeframe_end_date = self.user_profile["timeframe"]["end_date"]
        
        event_date_str = self.event_details["date_of_event"]
        event_date = None
        if event_date_str:
            event_date = datetime.strptime(event_date_str, "%d-%m-%Y")

        if timeframe_start_date and event_date < timeframe_start_date:
            return False
        if timeframe_end_date and event_date > timeframe_end_date:
            return False

        return True

    def _is_event_within_acceptable_price_range(self) -> bool:
        if self.event_details["price_of_event"] and self.user_profile["willingness_to_pay"]:
            if self.event_details["price_of_event"] > self.user_profile["budget"]:
                return False

        return True
    
    def _is_event_within_time_commitment(self) -> bool:
        if self.event_details["start_time"] and self.event_details["end_time"] and self.user_profile["time_commitment_in_minutes"]:
            start_time = datetime.strptime(self.event_details["start_time"], "%H:%M")
            end_time = datetime.strptime(self.event_details["end_time"], "%H:%M")
            time_difference = end_time - start_time
            if time_difference.total_seconds() > self.user_profile["time_commitment_in_minutes"] * 60:
                return False

        return True
