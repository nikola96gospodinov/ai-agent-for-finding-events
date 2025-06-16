import os
from dotenv import load_dotenv, find_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

if os.path.exists('.env'):
    load_dotenv(find_dotenv(), override=True)

local_model = ChatOllama(model="gemma3:12b", temperature=0.0)

# Great free model - free to use for 14,4k requests per day
great_free_model = ChatGoogleGenerativeAI(
    model='gemma-3-27b-it',
    api_key=os.environ["GEMINI_API_KEY"], # type: ignore
    temperature=0.0 
)
try:
    great_free_model.invoke("Hello")
    print("Google Generative AI is working")
except Exception as e:
    print(f"Error connecting to Google Generative AI: {e}")
    # Fallback to local model if Google API fails
    powerful_model = local_model


# Powerful model - free to use for 1.5k requests per day
powerful_model = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash',
    api_key=os.environ["GEMINI_API_KEY"], # type: ignore
    temperature=0.0
)
try:
    powerful_model.invoke("Hello")
    print("Google Generative AI is working")
except Exception as e:
    print(f"Error connecting to Google Generative AI: {e}")
    # Fallback to local model if Google API fails
    powerful_model = local_model