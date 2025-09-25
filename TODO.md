# TODO List for AI Code Judge App

- [x] Create requirements.txt with dependencies (streamlit>=1.28.0, langchain>=0.0.350, langchain-groq, python-dotenv)
- [x] Create app.py with Streamlit UI, LangChain integration, and prompt engineering for general-purpose code review (language detection, syntax/logic errors, best practices, security/performance, suggestions, confidence scores)
- [x] Create TODO.md file to track progress
- [x] Set up Python virtual environment (venv)
- [x] Install dependencies from requirements.txt
- [x] Run the Streamlit app (streamlit run app.py) and verify functionality
- [x] Fix deprecation warnings by updating to RunnableSequence (prompt | llm) and invoke method
- [x] Update model to supported llama-3.1-8b-instant
- [x] Test LLM initialization with sample code
- [x] Test with sample code inputs (e.g., Python with syntax error, JavaScript, etc.) to ensure language detection and confidence scores work - LLM tested successfully, model updated
- [x] If issues arise, debug and fix (e.g., API key loading, LLM responses) - Fixed decommissioned model error
