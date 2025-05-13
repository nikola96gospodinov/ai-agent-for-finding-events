from typing import TypedDict, Literal
from datetime import datetime

class EventDetails(TypedDict, total=False):
    title: str
    age_range: str
    gender_bias: str
    sexual_orientation_bias: str
    relationship_status_bias: str
    date_of_event: str
    start_time: str
    end_time: str
    location_of_event: str
    price_of_event: float | int
    event_format: str

class Timeframe(TypedDict, total=False):
    start_date: datetime
    end_date: datetime

class DistanceThreshold(TypedDict, total=False):
    distance_threshold: int
    unit: Literal["km", "miles"]

class Location(TypedDict, total=False):
    latitude: float
    longitude: float

class UserProfile(TypedDict, total=False):
    interests: list[str]
    goals: list[str]
    occupation: str

    age: int
    gender: Literal["male", "female", "non-binary", "other"] 
    sexual_orientation: Literal["straight", "lesbian", "gay", "bisexual", "transgender", "other"] 
    relationship_status: Literal["single", "in a relationship"] 
    willingness_to_pay: bool 
    budget: Literal[0, 10, 20, 50, 100, 200, 500, 1000] 
    willingness_for_online: bool 
    excluded_times: list[str] 
    location: Location 
    distance_threshold: DistanceThreshold 
    time_commitment_in_minutes: int 
    timeframe: Timeframe 