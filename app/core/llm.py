from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

local_model = ChatOllama(model="gemma3:12b", temperature=0.0)

# Great free model - free to use for 14,4k requests per day
great_free_model = ChatGoogleGenerativeAI(
    model='gemma-3-27b-it',
    api_key=settings.GEMINI_API_KEY, # type: ignore
    temperature=0.0 
)
try:
    great_free_model.invoke("Hello")
    print("Gemma 3:27b is working")
except Exception as e:
    print(f"Error connecting to Google Generative AI: {e}")
    # Fallback to local model if Google API fails
    powerful_model = local_model


# # Powerful model - free to use for 250 requests per day
# powerful_model = ChatGoogleGenerativeAI(
#     model='gemini-2.5-flash',
#     api_key=settings.GEMINI_API_KEY, # type: ignore
#     temperature=0.0
# )
# try:
#     powerful_model.invoke("Hello")
#     print("Gemini 2.5 Flash is working")
# except Exception as e:
#     print(f"Error connecting to Google Generative AI: {e}")
#     # Fallback to local model if Google API fails
#     powerful_model = local_model