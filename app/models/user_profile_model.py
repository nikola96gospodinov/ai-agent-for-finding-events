from datetime import datetime
from typing import Literal, TypedDict
from app.models.bias_options import gender_bias_options, sexual_orientation_bias_options, relationship_status_bias_options

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
    email: str
    birth_date: datetime
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