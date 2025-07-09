from typing import Optional, Dict, Any, cast
from datetime import datetime
from app.models.user_profile_model import UserProfile
from app.utils.address_utils import get_address_coordinates
from app.utils.date_utils import time_to_string

def convert_to_user_profile(profile_data: Dict[str, Any], user_data: Optional[Dict[str, Any]] = None) -> UserProfile | None:
    """Convert database profile data to UserProfile model"""
    try:
        birthday = profile_data.get('birthday')
        if isinstance(birthday, str):
            birth_date = datetime.fromisoformat(birthday)
        elif birthday and hasattr(birthday, 'date'):  # If it's a date object
            birth_date = datetime.combine(birthday, datetime.min.time())
        else:
            birth_date = datetime(1995, 1, 1)  # Default fallback
        
        weekday_start = profile_data.get('weekday_start_time')
        weekday_end = profile_data.get('weekday_end_time')
        weekend_start = profile_data.get('weekend_start_time')
        weekend_end = profile_data.get('weekend_end_time')
        
        acceptable_times = {
            "weekdays": {
                "start": time_to_string(weekday_start) or "17:00",
                "end": time_to_string(weekday_end) or "22:00"
            },
            "weekends": {
                "start": time_to_string(weekend_start) or "8:00",
                "end": time_to_string(weekend_end) or "23:00"
            }
        }
        
        distance_threshold = {
            "distance_threshold": profile_data.get('distance_threshold_value', 20),
            "unit": profile_data.get('distance_threshold_unit', 'miles')
        }
        
        location = get_address_coordinates(profile_data.get('postcode'))
        
        budget_value = profile_data.get('budget', 0)
        willingness_to_pay = budget_value > 0
        
        time_commitment_in_minutes = profile_data.get('time_commitment_in_minutes', 240)
        
        # Get email from user data (auth) or profile data, with fallback to empty string
        email = ""
        if user_data and user_data.get('email'):
            email = user_data.get('email')
        
        return cast(UserProfile, {
            "birth_date": birth_date,
            "gender": profile_data.get('gender', 'male'),
            "sexual_orientation": profile_data.get('sexual_orientation', 'straight'),
            "relationship_status": profile_data.get('relationship_status', 'single'),
            "willingness_to_pay": willingness_to_pay,
            "budget": budget_value,
            "willingness_for_online": profile_data.get('willingness_for_online', False),
            "acceptable_times": acceptable_times,
            "location": location,
            "distance_threshold": distance_threshold,
            "time_commitment_in_minutes": time_commitment_in_minutes,
            "interests": profile_data.get('interests', []),
            "goals": profile_data.get('goals', []),
            "occupation": profile_data.get('occupation', ''),
            "email": email
        })
    except Exception as e:
        print(f"Error converting profile data: {e}")
        return None
