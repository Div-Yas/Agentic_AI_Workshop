from setuptools import setup, find_packages

setup(
    name="bank_reconciliation",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langchain-google-genai",
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pandas",
        "streamlit",
        "python-dotenv",
        "requests"
    ],
) 