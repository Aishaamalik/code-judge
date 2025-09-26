import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

def initialize_llm() -> ChatGroq:
    """
    Initializes the Groq Language Model with the provided API key and model configuration.
    
    Returns:
        ChatGroq: Initialized Groq LLM instance.
    
    Raises:
        ValueError: If the API key is not found in the environment variables.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file. Please ensure it's set.")
    
    return ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",  # Updated to supported model
        temperature=0.1,  # Low temperature for consistent, factual responses
    )


def create_prompt_template() -> PromptTemplate:
    """
    Creates a PromptTemplate for analyzing code with detailed instructions for AI.
    
    Returns:
        PromptTemplate: A LangChain PromptTemplate object for code analysis.
    """
    prompt_template = """
    You are an expert AI code judge. Analyze the following code snippet provided by the user in detail.
    
    Instructions:
    1. Detect the programming language of the code (e.g., Python, JavaScript, Java, C++, etc.). If unclear, suggest the most likely one.
    2. Perform a comprehensive review:
       - Check for syntax errors: Identify any syntax issues and explain them clearly.
       - Check for logical errors or bugs: Point out potential runtime issues, infinite loops, incorrect logic, etc.
       - Review best practices: Suggest improvements for code style, readability, efficiency, and maintainability.
       - Security and performance: Highlight any vulnerabilities (e.g., SQL injection, buffer overflows) or performance bottlenecks.
       - Code smells: Identify common code smells like long methods, high complexity, duplicate code, etc.
       - Refactoring suggestions: Provide specific refactoring ideas to improve structure, such as extracting methods, applying design patterns, or reducing duplication.
       - Metrics analysis: Estimate or discuss key code metrics like cyclomatic complexity, maintainability index, lines of code, comment density, Halstead metrics (vocabulary, volume, difficulty), and readability (Flesch-Kincaid grade level). Suggest thresholds for good/bad values.
       - Suggestions: Provide specific, actionable fixes or refactored code examples where helpful.
    3. Structure your response with clear sections using Markdown formatting, emojis for visual appeal (✅ for no issues, ⚠️ for warnings, 🔴 for errors), bullet points, and tables where appropriate (e.g., for issues, metrics, and recommendations). Use the following exact headings:
       - ### Language Detected
       - ### Syntax Errors
       - ### Logical Issues/Bugs
       - ### Code Smells
       - ### Best Practices & Improvements
       - ### Security & Performance Concerns
       - ### Code Metrics
       - ### Refactoring Suggestions
       - ### Overall Suggestions
    4. Provide confidence scores (0-100%) for each major section, e.g., "Syntax Analysis Confidence: 95%". Base scores on how clear the code is and your certainty. Suggest key metrics for visualization if possible (e.g., complexity score, maintainability).

    Code to analyze:
    {code}

    Respond in a helpful, professional tone. Be thorough, detailed, and concise, focusing on visual structure for better readability. Prioritize actionable insights.
    """

    return PromptTemplate(
        input_variables=["code"],
        template=prompt_template,
    )


def create_analysis_chain():
    """
    Creates and returns the complete LLM analysis chain using the prompt template and initialized LLM.
    
    Returns:
        RunnableSequence: A complete analysis chain ready for invocation.
    """
    llm = initialize_llm()
    prompt = create_prompt_template()
    
    return prompt | llm
