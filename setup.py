import setuptools

setuptools.setup(
    name="GDER-Agent",
    version="0.0.1",
    packages=setuptools.find_packages(),
    install_requires=[
        "beautifulsoup4==4.13.5",
        "fastapi==0.116.1",
        "google-api-python-client==2.181.0",
        "google-auth-httplib2==0.2.0",
        "google-auth-oauthlib==1.2.2",
        "python-dotenv==1.1.1",
        "langchain-openai==0.3.32",
        "langgraph==0.6.6",
        "openpyxl==3.1.5",
        "pandas==2.3.2", 
        "uvicorn==0.35.0",
    ],
    python_requires=">=3.11",
)
