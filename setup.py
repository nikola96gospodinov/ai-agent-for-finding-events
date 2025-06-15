from setuptools import setup, find_packages

setup(
    name="ai-agents-intro",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain-ollama",
        "langchain-google-genai",
        "python-dotenv",
        "fastapi",
        "uvicorn",
        "pydantic",
        "pydantic-settings",
        "sqlalchemy",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
    ],
    python_requires=">=3.10",
) 