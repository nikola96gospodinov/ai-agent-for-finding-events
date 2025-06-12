from avatars import user_profile_main
from disqualify_event import EventDisqualifier
from custom_typings import EventDetails

# Create event details with corrected types
event = {
    'title': 'Travel & Hospitality Tech Startup Founder Innovation Pitch at Stripe',
    'age_range': None,
    'gender_bias': None,
    'sexual_orientation_bias': None,
    'relationship_status_bias': None,
    'date_of_event': '26-06-2025',
    'start_time': '18:00',
    'end_time': '20:30',
    'location_of_event': {
        'full_address': '201 Bishopsgate, 201 Broadgate London EC2M 3UN',
        'latitude': 51.5210268,
        'longitude': -0.0792583
    },
    'price_of_event': 0,
    'event_format': "offline",
    'is_sold_out': False
}

ed = EventDisqualifier(user_profile_main)

# Check overall compatibility
print(f"Overall compatibility: {ed.check_compatibility(event)}")

# Check each condition individually
checks = [
    ed._is_event_sold_out,
    ed._is_event_within_acceptable_distance,
    ed._is_event_within_acceptable_timeframe,
    ed._is_event_within_acceptable_price_range,
    ed._is_event_within_time_commitment,
    ed._is_event_within_acceptable_age_range,
    ed._is_event_suitable_for_gender,
    ed._is_event_suitable_for_sexual_orientation,
    ed._is_event_suitable_for_relationship_status,
    ed._is_event_suitable_for_event_format,
    ed._is_event_within_acceptable_times,
    ed._is_past_event,
    ed._is_event_page_empty
]

for check in checks:
    result = check(event)
    print(f"{check.__name__}: {result}")

# Debug the all() expression directly
check_results = [check(event) for check in checks]
print("\nAll check results:", check_results)
print("all() result:", all(check_results))

# Monkey patch the check_compatibility method to see exactly what's happening
original_check_compatibility = EventDisqualifier.check_compatibility

def debug_check_compatibility(self, event_details):
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
        self._is_event_within_acceptable_times,
        self._is_past_event,
        self._is_event_page_empty
    ]
    
    results = []
    for check in checks:
        result = check(event_details)
        print(f"Inside check_compatibility - {check.__name__}: {result}")
        results.append(result)
    
    final_result = all(results)
    print(f"Inside check_compatibility - final result: {final_result}")
    return final_result

# Replace the method temporarily
EventDisqualifier.check_compatibility = debug_check_compatibility

print("\nRunning with patched check_compatibility:")
print(f"Overall compatibility: {ed.check_compatibility(event)}")

# Restore the original method
EventDisqualifier.check_compatibility = original_check_compatibility 