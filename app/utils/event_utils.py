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