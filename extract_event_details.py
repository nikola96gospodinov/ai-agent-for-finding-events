from datetime import datetime
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
import ast

from custom_typings import EventDetails

def extract_event_details(webpage_content: str, model: BaseChatModel) -> EventDetails | None:
    extract_details_template = """
        The web page content is as follows:
        {webpage_content}

        Before extracting the details, check if the event is sold out, out of spaces, or on the same day as today. Today is {current_date}.
        If any of these conditions are met, the overall response should be set to None and there will be no need for details to be extracted.
        "Sales ending soon", "Sales end soon", "Limited spaces left", "Limited availability", "Limited availability left", or similar phrases are not a sign of a sold out event and details should be extracted.

        Extract the details of the event from the web page.
        The details that I need are:
        - Title of the event
        - Age range 
        - Gender bias - return "women only", "men only", or other specific gender designation if:
            * The event explicitly states it's for a specific gender
            * The event description uses gendered language throughout (e.g., "ladies", "sisterhood", "brotherhood")
            * The event focuses on experiences unique to a specific gender
            * The event is hosted by a gender-specific organization (e.g., "Women in Tech")
            * Marketing materials exclusively show one gender
            * The event addresses topics that are explicitly framed as gender-specific
        - Sexual orientation bias - for example if the event is tailored to LGBTQ+ only, then the sexual orientation bias should be "LGBTQ+ only". If there are no sexual orientation bias, then it should be None
        - Relationship status bias - for example if the event is tailored to singles only, then the relationship status bias should be "singles only". If there are no relationship status bias, then it should be None. Party nights are generally tailored to singles.
        - Date of the event - this should be in the following format: "DD-MM-YYYY". If the year of the event is not mentioned, then assume it's the current year - {current_year}. If there are multiple dates, then return the most relevant but never multiple dates. For example "14-01-2025 to 14-06-2025" should be "14-01-2025"
        - Start time of the event - this should be in the following format: "10:00", "22:00". Note that the time could be represented in many different ways on the page. 6, 6:00pm, 18:00 etc. but we need to extract the time in 24 hour format.
        - End time of the event - this should be in the following format: "10:00", "22:00". Note that the time could be represented in many different ways on the page. 6, 6:00pm, 18:00 etc. but we need to extract the time in 24 hour format.
        - Location of the event - be as specific as possible. For example, "123 Main St, EC1A 1BB, London, UK" is more specific than "London, UK". If the street is not mentioned, then the postcode is the most important thing.
        - Price of the event - just put the number like 20, 50, 100, etc. in either float or int format without the currency symbol. If an event is free, then the price should be 0 instead of None
        - Whether the event is online, in person or both. Mentions of Zoom, Online, Virtual, etc. should be considered online unless it's a combination of in person and online, in which case it should be "both".

        The response should be None if there is something to indicate so, or a Python dictionary:
        Example:
        {{
            "title": "Event Title",
            "age_range": "25-35",
            "gender_bias": "women only",
            "sexual_orientation_bias": "LGBTQ+ only",
            "relationship_status_bias": "singles only",
            "date_of_event": "06-01-2025",
            "start_time": "10:00",
            "end_time": "12:00",
            "location_of_event": "123 Main St, EC1A 1BB, London, UK",
            "price_of_event": "20",
            "event_format": "offline"
        }}
        Don't do any formatting. Just return the Python dictionary as plain text. Under any circumstances, don't use ```python or ``` in the response.

        If there is no information about a particular detail, return None for that detail.
    """

    event_details_prompt = ChatPromptTemplate.from_template(extract_details_template)
    event_details_chain = event_details_prompt | model

    event_details = event_details_chain.invoke({
        "webpage_content": webpage_content,
        "current_year": datetime.now().year,
        "current_date": datetime.now().strftime("%d-%m-%Y")
    })

    if hasattr(event_details, 'content'):
        event_details = event_details.content
    
    # Sometimes the model doesn't play along
    if isinstance(event_details, str) and (event_details.startswith("```python") or event_details.endswith("```")):
        event_details = event_details.replace("```python", "").replace("```", "")
    
    try:
        event_details_result: EventDetails | None = ast.literal_eval(event_details)
    except (SyntaxError, ValueError):
        event_details_result = None

    print("Event details:")
    print(event_details_result)

    return event_details_result