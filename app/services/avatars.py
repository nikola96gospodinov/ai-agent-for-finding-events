from datetime import datetime

from app.models.user_profile_model import UserProfile

user_profile_main: UserProfile = {
    "birth_date": datetime(1996, 6, 14),
    "gender": "male",
    "sexual_orientation": "straight",
    "relationship_status": "in a relationship",
    "willingness_to_pay": True,
    "budget": 50,
    "willingness_for_online": False,
    "acceptable_times": {
        "weekdays": {
            "start": "17:00",
            "end": "22:00"
        },
        "weekends": {
            "start": "8:00",
            "end": "23:00"
        }
    },
    "location": {
        "latitude": 51.5253263,
        "longitude": -0.1015115
    },
    "distance_threshold": {
        "distance_threshold": 20,
        "unit": "miles"
    },
    "time_commitment_in_minutes": 240, # 4 hours
    "interests": ["technology", "coding", "JavaScript", "Python", "AI", "startups", "business", "entrepreneurship", "Formula 1", "motorsports", "go karting", "football", "health", "fitness", "biohacking", "hiking", "nature", "outdoors", "latin dancing", "alcohol free", "phone free", "architecture", "interior design"],
    "goals": ["make new friends", "find a business partner"],
    "occupation": "software engineer",
    "email": "nikola96gospodinov@gmail.com"
}

user_profile_creative: UserProfile = {
    "birth_date": datetime(1991, 4, 1),
    "gender": "female",
    "sexual_orientation": "bisexual",
    "relationship_status": "single",
    "willingness_to_pay": True,
    "budget": 50,
    "willingness_for_online": True,
    "acceptable_times": {
        "weekdays": {
            "start": "18:00",
            "end": "23:00"
        },
        "weekends": {
            "start": "10:00",
            "end": None
        }
    },
    "location": {
        "latitude": 51.5495,
        "longitude": 0.0597
    },
    "distance_threshold": {
        "distance_threshold": 15,
        "unit": "miles"
    },
    "time_commitment_in_minutes": 360,
    "interests": ["art", "photography", "design", "music", "concerts", "theater", "poetry", "writing", "coffee", "vegan", "sustainability", "travel", "yoga", "meditation", "breathwork", "art", "exhibitions", "museums"],
    "goals": ["find creative collaborators", "expand social circle", "discover new art venues", "find a romantic partner"],
    "occupation": "graphic designer",
    "email": "nikola96gospodinov@gmail.com"
}

user_profile_sports: UserProfile = {
    "birth_date": datetime(1998, 10, 15),
    "gender": "male",
    "sexual_orientation": "straight",
    "relationship_status": "single",
    "willingness_to_pay": False,
    "budget": 20,
    "willingness_for_online": False,
    "acceptable_times": {
        "weekdays": {
            "start": "19:00",
            "end": "22:00"
        },
        "weekends": {
            "start": "9:00",
            "end": "23:00"
        }
    },
    "location": {
        "latitude": 51.5386,
        "longitude": 0.1028
    },
    "distance_threshold": {
        "distance_threshold": 10,
        "unit": "miles"
    },
    "time_commitment_in_minutes": 180,
    "interests": ["football", "basketball", "running", "gym", "fitness", "sports", "healthy eating", "team sports", "outdoor activities", "hiking", "cycling", "swimming", "yoga", "meditation", "breathwork"],
    "goals": ["join local teams", "improve fitness"],
    "occupation": "personal trainer",
    "email": "nikola96gospodinov@gmail.com"
}

user_profile_family: UserProfile = {
    "birth_date": datetime(1983, 7, 10),
    "gender": "female",
    "sexual_orientation": "straight",
    "relationship_status": "married",
    "willingness_to_pay": True,
    "budget": 100,
    "willingness_for_online": True,
    "acceptable_times": {
        "weekdays": {
            "start": "20:00",
            "end": "22:00"
        },
        "weekends": {
            "start": "14:00",
            "end": "18:00"
        }
    },
    "location": {
        "latitude": 51.5390,
        "longitude": 0.1426
    },
    "distance_threshold": {
        "distance_threshold": 10,
        "unit": "miles"
    },
    "time_commitment_in_minutes": 120,
    "interests": ["parenting", "cooking", "gardening", "reading", "board games", "family activities", "local community", "volunteering"],
    "goals": ["find family-friendly activities", "build local connections"],
    "occupation": "teacher",
    "email": "nikola96gospodinov@gmail.com"
}

user_profile_student: UserProfile = {
    "birth_date": datetime(2005, 1, 14),
    "gender": "non-binary",
    "sexual_orientation": "other",
    "relationship_status": "single",
    "willingness_to_pay": False,
    "budget": 0,
    "willingness_for_online": True,
    "acceptable_times": {
        "weekdays": {
            "start": "16:00",
            "end": "23:00"
        },
        "weekends": {
            "start": "12:00",
            "end": None
        }
    },
    "location": {
        "latitude": 51.4773,
        "longitude": 0.2017
    },
    "distance_threshold": {
        "distance_threshold": 25,
        "unit": "miles"
    },
    "time_commitment_in_minutes": 240,
    "interests": ["studying", "campus life", "student activities", "music", "gaming", "social media", "cafe culture", "budget travel", "clubbing", "nightlife", "dancing", "dating"],
    "goals": ["make study buddies", "find campus events", "network with peers", "dating"],
    "occupation": "university student",
    "email": "nikola96gospodinov@gmail.com"
}

user_profile_main_other: UserProfile = {
    "birth_date": datetime(1987, 7, 14),
    "gender": "female",
    "sexual_orientation": "straight",
    "relationship_status": "in a relationship",
    "willingness_to_pay": True,
    "budget": 20,
    "willingness_for_online": False,
    "acceptable_times": {
        "weekdays": {
            "start": "17:00",
            "end": "22:00"
        },
        "weekends": {
            "start": "8:00",
            "end": "23:00"
        }
    },
    "location": {
        "latitude": 51.5253263,
        "longitude": -0.1015115
    },
    "distance_threshold": {
        "distance_threshold": 20,
        "unit": "miles"
    },
    "time_commitment_in_minutes": 240,
    "interests": ["reading", "sci-fi", "running", "travel", "coffee", "art", "music", "museums", "swimming", "phone free", "hiking", "nature", "outdoors", "psychology", "tattoos", "fashion", "movies", "cinematography", "talks"],
    "goals": ["find a new job"],
    "occupation": "nurse",
    "email": "nikola96gospodinov@gmail.com"
}