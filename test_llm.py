import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Test LLM initialization
try:
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        print("Error: GROQ_API_KEY not found in .env file.")
    else:
        print("API key found. Testing LLM initialization...")
        llm = ChatGroq(
            api_key=groq_api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=100
        )
        response = llm.invoke("Hello, how are you?")
        print("LLM test successful. Response:", response.content)
except Exception as e:
    print(f"Error: {e}")
