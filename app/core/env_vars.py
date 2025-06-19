from dotenv import load_dotenv, find_dotenv
import os

if os.path.exists('.env'):
    load_dotenv(find_dotenv(), override=True)

def get_env_var(var_name: str) -> str | None:
    return os.getenv(var_name)