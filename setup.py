from setuptools import setup, find_packages

setup(
    name="ai-agents-intro",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain-ollama",
        "langchain-google-genai",
        "python-dotenv",
    ],
    python_requires=">=3.10",
) 