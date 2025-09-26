import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

def initialize_llm(temperature: float = 0.1) -> ChatGroq:
    """
    Initializes the Groq Language Model with the provided API key and model configuration.

    Args:
        temperature (float): Temperature for the LLM (0.0 to 1.0).

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
        temperature=temperature,  # Configurable temperature
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
       - Metrics analysis: Estimate or discuss key code metrics like cyclomatic complexity, maintainability index, lines of code, comment density, Halstead metrics (vocabulary, volume, difficulty), readability (Flesch-Kincaid grade level), nesting depth, function count, variable count, code duplication. Suggest thresholds for good/bad values.
       - Dependency analysis: Identify potential external dependencies (libraries, frameworks) and suggest alternatives or security checks.
       - Test coverage estimation: Estimate how well the code might be covered by unit tests and suggest areas needing more tests.
       - Time/Space complexity estimation: Analyze algorithmic complexity where applicable (e.g., loops, recursion) and estimate Big O notation.
       - Code duplication detection: Identify duplicated code blocks and suggest consolidation.
       - Suggestions: Provide specific, actionable fixes or refactored code examples where helpful.
    3. Structure your response with clear sections using Markdown formatting, emojis for visual appeal (✅ for no issues, ⚠️ for warnings, 🔴 for errors), bullet points, and tables where appropriate (e.g., for issues, metrics, and recommendations). Use the following exact headings:
       - ### Language Detected
       - ### Syntax Errors
       - ### Logical Issues/Bugs
       - ### Code Smells
       - ### Best Practices & Improvements
       - ### Security & Performance Concerns
       - ### Code Metrics
       - ### Dependency Analysis
       - ### Test Coverage Estimation
       - ### Time/Space Complexity Estimation
       - ### Code Duplication Detection
       - ### Refactoring Suggestions
       - ### Overall Suggestions
    4. Provide confidence scores (0-100%) for each major section, e.g., "Syntax Analysis Confidence: 95%". Base scores on how clear the code is and your certainty. Include confidence for new sections like "Dependency Analysis Confidence: 85%". Suggest key metrics for visualization if possible (e.g., complexity score, maintainability).

    Code to analyze:
    {code}

    Respond in a helpful, professional tone. Be thorough, detailed, and concise, focusing on visual structure for better readability. Prioritize actionable insights.
    """

    return PromptTemplate(
        input_variables=["code"],
        template=prompt_template,
    )


def create_multi_file_prompt_template() -> PromptTemplate:
    """
    Creates a shorter PromptTemplate for multi-file analysis to reduce token usage.
    
    Returns:
        PromptTemplate: A LangChain PromptTemplate object for code analysis.
    """
    prompt_template = """
    You are an expert AI code judge. Analyze the following code snippet briefly for project-level insights.

    Instructions:
    1. Detect the programming language.
    2. Perform a review:
       - Syntax errors.
       - Logical issues/bugs.
       - Best practices & improvements.
       - Security & performance concerns.
       - Code smells.
       - Key metrics: lines of code, cyclomatic complexity, maintainability index, readability.
       - Refactoring suggestions.
    3. Structure response with clear sections using Markdown, emojis. Use headings:
       - ### Language Detected
       - ### Syntax Errors
       - ### Logical Issues/Bugs
       - ### Best Practices & Improvements
       - ### Security & Performance Concerns
       - ### Code Metrics
       - ### Refactoring Suggestions
    4. Be concise, focus on actionable insights.

    Code to analyze:
    {code}

    """
    return PromptTemplate(
        input_variables=["code"],
        template=prompt_template,
    )


def create_analysis_chain(temperature: float = 0.1):
    """
    Creates and returns the complete LLM analysis chain using the prompt template and initialized LLM.

    Args:
        temperature (float): Temperature for the LLM (0.0 to 1.0).

    Returns:
        RunnableSequence: A complete analysis chain ready for invocation.
    """
    llm = initialize_llm(temperature)
    prompt = create_prompt_template()

    return prompt | llm


def create_multi_file_analysis_chain(custom_prompt=None, temperature: float = 0.1):
    """
    Creates and returns the multi-file analysis chain with optional custom prompt.
    If custom_prompt is provided, uses it; otherwise, uses the default shorter prompt.

    Args:
        custom_prompt (str, optional): Custom prompt template string with {code} placeholder.
        temperature (float): Temperature for the LLM (0.0 to 1.0).

    Returns:
        RunnableSequence: A complete analysis chain ready for invocation.
    """
    llm = initialize_llm(temperature)
    if custom_prompt:
        prompt = PromptTemplate(
            input_variables=[],
            template=custom_prompt,
        )
    else:
        prompt = create_multi_file_prompt_template()

    return prompt | llm
