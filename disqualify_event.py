from typings import EventDetails, UserProfile
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

class EventDisqualifier:
    def __init__(self, event_details: EventDetails, user_profile: UserProfile, model: OllamaLLM):
        self.event_details = event_details
        self.user_profile = user_profile
        self.model = model

    def _check_compatibility(self, event_restriction, user_characteristic) -> bool:
        prompt_template = """
            You are a helpful assistant that determines if an event is disqualifying for a user. If it is, you should return "True". If it is not, you should return "False".

            The event has the following restriction:
            {event_restriction}

            The user has the following characteristic:
            {user_characteristic}
        """

        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.model
        response = chain.invoke({"event_restriction": event_restriction, "user_characteristic": user_characteristic})
        return response.strip().lower() == "true"

    # TODO: Function that will use Geocoding API to check if the event is in the user's threshold for distance
    def _is_event_within_acceptable_distance(self) -> bool:
        return True

    def _is_event_for_the_right_age_range(self) -> bool:
        if self.event_details["age_range"] and self.user_profile["age"]:
            return self._check_compatibility(self.event_details["age_range"], self.user_profile["age"])
        return True
    
    def _is_event_for_the_right_gender(self) -> bool:
        if self.event_details["gender_bias"] and self.user_profile["gender"]:
            return self._check_compatibility(self.event_details["gender_bias"], self.user_profile["gender"])
        return True

    def _is_event_for_the_right_sexual_orientation(self) -> bool:
        if self.event_details["sexual_orientation_bias"] and self.user_profile["sexual_orientation"]:
            return self._check_compatibility(self.event_details["sexual_orientation_bias"], self.user_profile["sexual_orientation"])
        return True
    
    def _is_event_for_the_right_relationship_status(self) -> bool:
        if self.event_details["relationship_status_bias"] and self.user_profile["relationship_status"]:
            return self._check_compatibility(self.event_details["relationship_status_bias"], self.user_profile["relationship_status"])
        return True
    
    
    def _is_event_price_compatible(self) -> bool:
        return True
