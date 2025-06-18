import datetime

def remove_duplicates_based_on_title(events: list[dict]) -> list[dict]:
    unique_events = []
    seen_titles = set()
    for event in events:
        if event["title"] not in seen_titles:
            unique_events.append(event)
            seen_titles.add(event["title"])

    return unique_events

def remove_events_with_negative_relevance(events: list[dict]) -> list[dict]:
    return [event for event in events if event["relevance"] > 0]

def get_seconds_until_event(date_of_event: str | None, start_time: str | None) -> int:
    """
    Calculate the number of seconds from now until the event starts, based on date_of_event and start_time.
    If parsing fails or the event is in the past, return A_DAY_IN_SECONDS.
    """
    A_DAY_IN_SECONDS = 24 * 60 * 60

    if not date_of_event or not start_time:
        return A_DAY_IN_SECONDS
    try:
        dt_str = f"{date_of_event} {start_time}"
        event_dt = datetime.datetime.strptime(dt_str, "%d-%m-%Y %H:%M")
        now = datetime.datetime.now()
        delta = (event_dt - now).total_seconds()
        if delta > 0:
            return int(delta)
        else:
            return A_DAY_IN_SECONDS
    except Exception as e:
        print(f"Error parsing event datetime: {e}")
        return A_DAY_IN_SECONDS