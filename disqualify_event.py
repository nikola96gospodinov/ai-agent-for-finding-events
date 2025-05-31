from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime, timedelta

from custom_typings import EventDetails, UserProfile, Location
from utils import calculate_distance

class EventDisqualifier:
    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile

    def check_compatibility(self, event_details: EventDetails) -> bool:
        # Check all quick conditions first
        checks = [
            self._is_event_sold_out,
            self._is_event_within_acceptable_distance,
            self._is_event_within_acceptable_timeframe,
            self._is_event_within_acceptable_price_range,
            self._is_event_within_time_commitment,
            self._is_event_within_acceptable_age_range,
            self._is_event_suitable_for_gender,
            self._is_event_suitable_for_sexual_orientation,
            self._is_event_suitable_for_relationship_status,
            self._is_event_suitable_for_event_format,
            self._is_event_within_acceptable_times
        ]
        
        return all(check(event_details) for check in checks)
    
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
        timeframe_start_date = self.user_profile["timeframe"].get("start_date")
        timeframe_end_date = self.user_profile["timeframe"].get("end_date")
        
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
    
    def _is_event_suitable_for_relationship_status(self, event_details: EventDetails) -> bool:
        if event_details["relationship_status_bias"] and self.user_profile["relationship_status"]:
            if self.user_profile["relationship_status"] not in event_details["relationship_status_bias"]:
                print("Event is not suitable for the user's relationship status")
                return False

        return True
    
    def _is_event_suitable_for_event_format(self, event_details: EventDetails) -> bool:
        if not event_details["event_format"] or "willingness_for_online" not in self.user_profile:
            return True
            
        if not self.user_profile["willingness_for_online"] and "online" in event_details["event_format"] and "offline" not in event_details["event_format"]:
            print("Event is online-only and the user is unwilling to attend online events")
            return False

        return True
    
    def _is_event_within_acceptable_times(self, event_details: EventDetails) -> bool:
        is_weekday = event_details["date_of_event"] and datetime.strptime(event_details["date_of_event"], "%d-%m-%Y").weekday() < 5

        if is_weekday:
            weekday_start_time = self.user_profile["acceptable_times"]["weekdays"]["start"]
            if event_details["start_time"] and weekday_start_time:
                start_time = datetime.strptime(event_details["start_time"], "%H:%M")
                start_time_user = datetime.strptime(weekday_start_time, "%H:%M")
                # Add 30 minutes padding to start time
                start_time_user = start_time_user - timedelta(minutes=30)
                if start_time < start_time_user:
                    print("Event is before the user's acceptable times")
                    return False
            
            weekday_end_time = self.user_profile["acceptable_times"]["weekdays"]["end"]
            if event_details["end_time"] and weekday_end_time:
                end_time = datetime.strptime(event_details["end_time"], "%H:%M")
                end_time_user = datetime.strptime(weekday_end_time, "%H:%M")
                # Add 30 minutes padding to end time
                end_time_user = end_time_user + timedelta(minutes=30)
                if end_time > end_time_user:
                    print("Event is after the user's acceptable times")
                    return False

        else:
            weekend_start_time = self.user_profile["acceptable_times"]["weekends"]["start"]
            if event_details["start_time"] and weekend_start_time:
                start_time = datetime.strptime(event_details["start_time"], "%H:%M")
                start_time_user = datetime.strptime(weekend_start_time, "%H:%M")
                # Add 30 minutes padding to start time
                start_time_user = start_time_user - timedelta(minutes=30)
                if start_time < start_time_user:
                    print("Event is before the user's acceptable times")
                    return False
            
            weekend_end_time = self.user_profile["acceptable_times"]["weekends"]["end"]
            if event_details["end_time"] and weekend_end_time:
                end_time = datetime.strptime(event_details["end_time"], "%H:%M")
                end_time_user = datetime.strptime(weekend_end_time, "%H:%M")
                # Add 30 minutes padding to end time
                end_time_user = end_time_user + timedelta(minutes=30)
                if end_time > end_time_user:
                    print("Event is after the user's acceptable times")
                    return False

        return True