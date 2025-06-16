def get_age_bracket(age: int) -> str:
    decade = (age // 10) * 10

    if age < 20:
        return "teens"
    
    return f"{decade}s"