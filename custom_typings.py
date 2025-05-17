from typing import TypedDict, Literal
from datetime import datetime

class LocationOfEvent(TypedDict, total=False):
    latitude: float
    longitude: float
    full_address: str | None

class AgeRange(TypedDict):
    min_age: int | None
    max_age: int | None

class EventDetails(TypedDict):
    title: str
    age_range: AgeRange | None
    gender_bias: str | None
    sexual_orientation_bias: str | None
    relationship_status_bias: str | None
    date_of_event: str | None
    start_time: str | None
    end_time: str | None
    location_of_event: LocationOfEvent
    price_of_event: float | int
    event_format: str | None

class Timeframe(TypedDict):
    start_date: datetime
    end_date: datetime

DistanceUnit = Literal["km", "miles"]

class DistanceThreshold(TypedDict):
    distance_threshold: int
    unit: DistanceUnit

class Location(TypedDict, total=False):
    latitude: float
    longitude: float

class UserProfile(TypedDict):
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