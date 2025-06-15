from typing import Literal, TypedDict
from app.models.bias_options import gender_bias_options, sexual_orientation_bias_options, relationship_status_bias_options, event_format_options

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