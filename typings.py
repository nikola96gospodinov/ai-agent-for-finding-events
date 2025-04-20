from typing import TypedDict, Literal
from datetime import datetime

class EventDetails(TypedDict, total=False):
    age_range: str
    gender_bias: str
    sexual_orientation_bias: str
    relationship_status_bias: str
    start_time: str
    end_time: str
    location_of_event: str
    price_of_event: str
    event_format: str

class Timeframe(TypedDict, total=False):
    start_date: datetime
    end_date: datetime

class DistanceThreshold(TypedDict, total=False):
    distance_threshold: int
    unit: Literal["km", "miles"]

class UserProfile(TypedDict, total=False):
    interests: list[str]
    goals: list[str]
    occupation: str

    age: int
    gender: Literal["male", "female", "non-binary", "other"]
    sexual_orientation: Literal["straight", "lesbian", "gay", "bisexual", "transgender", "other"]
    relationship_status: Literal["single", "in a relationship"]
    willingness_to_pay: bool
    willingness_for_online: bool
    excluded_times: list[str]
    location: str
    distance_threshold: DistanceThreshold
    time_commitment: Literal["0 to 2 hours", "2 to 4 hours", "4 hours to 1 day", "a few days"]
    budget: Literal[0, 10, 20, 50, 100, 200, 500, 1000]
    timeframe: Timeframe