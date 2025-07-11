def time_to_string(time_obj):
    """
    Convert a time object or string to HH:MM format.
    Handles datetime objects, time objects, and strings (with or without seconds).
    Examples: "17:45:00" -> "17:45", "17:45" -> "17:45", time_obj -> "17:45"
    """
    if not time_obj:
        return None
    
    if hasattr(time_obj, 'strftime'):
        return time_obj.strftime('%H:%M')
    elif isinstance(time_obj, str):
        # Handle times that might include seconds (e.g., "17:45:00" -> "17:45")
        if time_obj.count(':') == 2:  # Has seconds
            return ':'.join(time_obj.split(':')[:2])
        return time_obj
    
    return None