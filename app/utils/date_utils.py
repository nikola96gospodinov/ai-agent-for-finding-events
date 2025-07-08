def time_to_string(time_obj):
    if time_obj:
        if hasattr(time_obj, 'strftime'):
            return time_obj.strftime('%H:%M')
        elif isinstance(time_obj, str):
            return time_obj
    return None