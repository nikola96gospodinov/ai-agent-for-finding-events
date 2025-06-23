from datetime import datetime

def get_age_bracket(age: int) -> str:
    decade = (age // 10) * 10

    if age < 20:
        return "teens"
    
    return f"{decade}s"

def get_age_from_birth_date(birth_date: datetime) -> int:
    today = datetime.now()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age