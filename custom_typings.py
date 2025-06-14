from typing import TypedDict, Literal
from datetime import datetime

gender_bias_options = Literal["male", "female", "non-binary", "other"]
sexual_orientation_bias_options = Literal["straight", "lesbian", "gay", "bisexual", "transgender", "other"]
relationship_status_bias_options = Literal["single", "in a relationship", "married", "divorced", "widowed", "polygamous", "other"]
event_format_options = Literal["offline", "online"]

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
    gender_bias: list[gender_bias_options] | None
    sexual_orientation_bias: list[sexual_orientation_bias_options] | None
    relationship_status_bias: list[relationship_status_bias_options] | None
    date_of_event: str | None
    start_time: str | None
    end_time: str | None
    location_of_event: LocationOfEvent
    price_of_event: float | int
    event_format: Literal[event_format_options] | None
    is_sold_out: bool | None

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

class StartEndTime(TypedDict):
    start: str | None
    end: str | None

class AcceptableTimes(TypedDict):
    weekdays: StartEndTime
    weekends: StartEndTime

class UserProfile(TypedDict):
    interests: list[str]
    goals: list[str]
    occupation: str

    age: int
    gender: gender_bias_options
    sexual_orientation: sexual_orientation_bias_options
    relationship_status: relationship_status_bias_options
    willingness_to_pay: bool 
    budget: Literal[0, 10, 20, 50, 100, 200, 500, 1000] 
    willingness_for_online: bool 
    acceptable_times: AcceptableTimes
    location: Location 
    distance_threshold: DistanceThreshold 
    time_commitment_in_minutes: int 
    timeframe: Timeframe

class Interests(TypedDict):
    exact_match: int
    partial_match: int
    weak_match: int
    
class Goals(TypedDict):
    exact_match: int
    partial_match: int
    weak_match: int

industry_mismatch_options = Literal["complete_mismatch", "significant_mismatch", "overly_broad_mismatch", "no_mismatch"]

class ScoringSystem(TypedDict):
    interests: Interests
    goals: Goals
    industry_mismatch: industry_mismatch_options