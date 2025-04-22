from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from typings import UserProfile

def calculate_event_relevance(webpage_content: str, user_profile: UserProfile, model: OllamaLLM) -> float:
    template = """
        The web page content is as follows:
        {webpage_content}

        You are a helpful personal assistant who evaluates web pages for relevance to a given user.
        Your task is to scan the web page and determine if it is relevant to the user. You should return a percentage (0 to 100) of how relevant the event is for the user. It's very important that the score is explicitly stated at the start of the response.
        After that, explain your reasoning behind the score.

        The user is a person who is looking for a events relevant to their interests and goals.

        Their occupation is just for context. It may be relevant but most of the time it's not.
        The user is a {occupation}.

        The user is interested in {interests} and the user's goals are {goals}. There needs to be at least one common interest (or a close match) between the user and the event for it to be relevant and it needs to be aligned with the user's goals. An event doesn't need to hit all of the interests and goals but rather some of them. The more close matches, the higher the score.
        Ignore very loose connections and indirect interests and goals. If there isn't at least one close match, the overall score should be 0.
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    # Include the webpage content in the prompt
    result = chain.invoke({
        "occupation": user_profile["occupation"],
        "interests": user_profile["interests"],
        "goals": user_profile["goals"],
        "webpage_content": webpage_content
    })
    print("\nRelevance score:")
    print(result)