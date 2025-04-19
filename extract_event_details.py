from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import ast
from typing import TypedDict

class EventDetails(TypedDict, total=False):
    age_range: str
    gender_bias: str
    sexual_orientation_bias: str
    relationship_status_bias: str
    start_time: str
    end_time: str
    location_of_event: str
    price_of_event: str
    event_format: str

def extract_event_details(webpage_content: str, model: OllamaLLM) -> EventDetails:
    extract_details_template = """
        The web page content is as follows:
        {webpage_content}

        Extract the details of the event from the web page.
        The details that I need are:
        - Age range 
        - Gender bias - return "women only", "men only", or other specific gender designation if:
            * The event explicitly states it's for a specific gender
            * The event description uses gendered language throughout (e.g., "ladies", "sisterhood", "brotherhood")
            * The event focuses on experiences unique to a specific gender
            * The event is hosted by a gender-specific organization (e.g., "Women in Tech")
            * Marketing materials exclusively show one gender
            * The event addresses topics that are explicitly framed as gender-specific
        - Sexual orientation bias - for example if the event is tailored to LGBTQ+ only, then the sexual orientation bias should be "LGBTQ+ only". If there are no sexual orientation bias, then it should be null
        - Relationship status bias - for example if the event is tailored to singles only, then the relationship status bias should be "singles only". If there are no relationship status bias, then it should be null
        - Start time of the event
        - End time of the event
        - Location of the event - be as specific as possible. For example, "123 Main St, Anytown, USA" is more specific than "Anytown, USA"
        - Price of the event - if an event is free, then the price should be "0" instead of None
        - Whether the event is online, in person or both

        The response should be a Python dictionary:
        Example:
        {{
            "age_range": "25-35",
            "gender_bias": "women only",
            "sexual_orientation_bias": "LGBTQ+ only",
            "relationship_status_bias": "singles only",
            "start_time": "10:00",
            "end_time": "12:00",
            "location_of_event": "London, UK",
            "price_of_event": "£20",
            "event_format": "offline"
        }}
        Don't do any formatting. Just return the Python dictionary as plain text. Under any circumstances, don't use ```python or ``` in the response.

        If there is no information about a particular detail, return None for that detail.
    """

    event_details_prompt = ChatPromptTemplate.from_template(extract_details_template)
    event_details_chain = event_details_prompt | model

    event_details = event_details_chain.invoke({
        "webpage_content": webpage_content
    })

    # Sometimes the model doesn't play along
    if event_details.startswith("```python") or event_details.startswith("```"):
        event_details = event_details.replace("```python", "").replace("```", "")
    event_details_dict: EventDetails = ast.literal_eval(event_details)

    return event_details_dict