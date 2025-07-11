def time_to_string(time_obj):
    if time_obj:
        if hasattr(time_obj, 'strftime'):
            return time_obj.strftime('%H:%M')
        elif isinstance(time_obj, str):
            return time_obj
    return None

def normalize_time_string(time_str: str) -> str:
    """
    Normalize a time string to HH:MM format by removing seconds if present.
    Handles times like "17:45:00" -> "17:45"
    """
    if not time_str:
        return time_str
    
    # Handle times that might include seconds (e.g., "17:45:00" -> "17:45")
    if time_str.count(':') == 2:  # Has seconds
        return ':'.join(time_str.split(':')[:2])
    
    return time_str