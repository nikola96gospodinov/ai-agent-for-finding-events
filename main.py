from datetime import datetime
from langchain_ollama.llms import OllamaLLM

from scrape_web_page import scrap_page
from extract_event_details import extract_event_details
from disqualify_event import EventDisqualifier
from typings import UserProfile

webpage_content = scrap_page("https://www.eventbrite.co.uk/e/lesbian-pub-night-hosted-by-lesbian-supper-club-tickets-1289891864289?aff=ebdssbdestsearch&keep_tld=1")

model = OllamaLLM(model="gemma3:12b")

event_details = extract_event_details(webpage_content, model)

user_profile: UserProfile = {
    "age": 28,
    "gender": "male",
    "sexual_orientation": "straight",
    "relationship_status": "in a relationship",
    "willingness_to_pay": True,
    "budget": 20,
    "willingness_for_online": False,
    "excluded_times": ["after 22:00", "before 9:00", "9-5 weekdays"],
    "location": "London, UK",
    "distance_threshold": 10,
    "time_commitment_in_minutes": 240,
    "timeframe": {
        "start_date": datetime(2025, 5, 1),
        "end_date": datetime(2025, 5, 31)
    },
    "interests": ["technology", "coding", "startups", "business", "entrepreneurship", "Formula 1", "motorsports", "go karting", "football", "health", "fitness", "hiking", "nature", "outdoors", "latin dancing", "alcohol free", "offline", "architecture", "interior design"],
    "goals": ["network professionally", "make new friends", "find a business partner"],
    "occupation": "software engineer"
}

event_disqualifier = EventDisqualifier(user_profile, model)
is_compatible = event_disqualifier.check_compatibility(event_details)

print(is_compatible)

# template = """
#     The web page content is as follows:
#     {webpage_content}

#     You are a helpful personal assistant who evaluates web pages for relevance to a given user.
#     Your task is to scan the web page and determine if it is relevant to the user. You should return a percentage (0 to 100) of how relevant the event is for the user. It's very important that the score is explicitly stated at the start of the response.
#     After that, explain your reasoning behind the score.

#     The user is a person who is looking for a events relevant to their interests and goals. Their age, gender, sexual orientation, willingness to pay, excluded times, willingness for online events, and relationship status are disqualifiers. 
#     If there are any disqualifiers, you should return an overall score of 0 unless there is an incredibly close match in terms of interests and goals but even then the score should be low - below 50%.

#     Their occupation is just for context. It is not a disqualifier nor a qualifier.
#     The user is a {occupation}.

#     The user is {age} years old. Do not use overly broad age ranges. For example, 28 to 49 is not acceptable.
#     The user is {gender}. Overall score should be 0 if it is not compatible with the user's gender.
#     The user is {sexual_orientation}. Overall score should be 0 if it is not compatible with the user's sexual orientation.
#     The user is {relationship_status}. Overall score should be 0 if it is not compatible with the user's relationship status. For example, if the user is in a relationship and the event is for singles only, the score should be 0.
#     The user is {willingness_to_pay} to pay for events.
#     The user is {willingness_for_online} to attend online events.
#     The user doesn't want to attend events {exclude_times}. All other times are fine.

#     The user is interested in {interests} and the user's goals are {goals}. There needs to be at least one common interest (or a close match) between the user and the event for it to be relevant and it needs to be aligned with the user's goals. An event doesn't need to hit all of the interests and goals but rather some of them. The more close matches, the higher the score.
#     Ignore very loose connections and indirect interests and goals. If there isn't at least one close match, the overall score should be 0.
# """
# prompt = ChatPromptTemplate.from_template(template)
# chain = prompt | model

# # Include the webpage content in the prompt
# result = chain.invoke({
#     "age": age, 
#     "gender": gender,
#     "sexual_orientation": sexual_orientation,
#     "relationship_status": relationship_status,
#     "exclude_times": exclude_times,
#     "willingness_to_pay": willingness_to_pay,
#     "willingness_for_online": willingness_for_online,
#     "occupation": occupation,
#     "interests": interests, 
#     "goals": goals,
#     "webpage_content": webpage_content
# })
# print("\nRelevance score:")
# print(result)