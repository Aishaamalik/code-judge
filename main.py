import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

import os

# Load environment variables
load_dotenv()

# Initialize Groq LLM
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY not found in .env file. Please ensure it's set.")
    st.stop()

llm = ChatGroq(
    groq_api_key=api_key,
    model_name="llama-3.1-8b-instant",  # Updated to supported model
    temperature=0.1,  # Low temperature for consistent, factual responses
)

# Prompt template for general-purpose code review
prompt_template = """
You are an expert AI code judge. Analyze the following code snippet provided by the user.

Instructions:
1. Detect the programming language of the code (e.g., Python, JavaScript, Java, C++, etc.). If unclear, suggest the most likely one.
2. Perform a comprehensive review:
   - Check for syntax errors: Identify any syntax issues and explain them clearly.
   - Check for logical errors or bugs: Point out potential runtime issues, infinite loops, incorrect logic, etc.
   - Review best practices: Suggest improvements for code style, readability, efficiency, and maintainability.
   - Security and performance: Highlight any vulnerabilities (e.g., SQL injection, buffer overflows) or performance bottlenecks.
   - Suggestions: Provide specific, actionable fixes or refactored code examples where helpful.
3. Structure your response with clear sections using Markdown formatting, emojis for visual appeal (✅ for no issues, ⚠️ for warnings, 🔴 for errors), bullet points, and tables where appropriate (e.g., for issues and recommendations). Use headings like ## Language Detected, ### Syntax Errors, etc.
   - Language Detected: Include confidence score.
   - Syntax Errors: (List if any with 🔴, else "None detected" with ✅)
   - Logical Issues/Bugs: (List if any with ⚠️ or 🔴, else "None detected" with ✅)
   - Best Practices & Improvements: Bullet points with suggestions.
   - Security & Performance Concerns: Highlight with emojis.
   - Overall Suggestions: Include refactored code in ``` blocks if relevant.
4. Provide confidence scores (0-100%) for each major section, e.g., "Syntax Analysis Confidence: 95%". Base scores on how clear the code is and your certainty. Suggest key metrics for visualization if possible (e.g., complexity score).

Code to analyze:
{code}

Respond in a helpful, professional tone. Be thorough but concise, focusing on visual structure for better readability.
"""

prompt = PromptTemplate(
    input_variables=["code"],
    template=prompt_template,
)

# Create LLM chain
chain = prompt | llm

# Streamlit UI
st.title("🤖 AI Code Judge")
st.write("Enter any code snippet below for a comprehensive AI-powered review. Supports multiple languages!")

code_input = st.text_area(
    "Paste your code here:",
    placeholder="""# Example Python code
def hello_world():
    print("Hello, World!")""",
    height=200,
)

if st.button("Analyze Code", type="primary"):
    if code_input.strip():
        with st.spinner("Analyzing your code..."):
            try:
                result = chain.invoke({"code": code_input})
                st.subheader("Analysis Results:")

                # Parse and display sections in collapsible expanders for better organization
                result_str = result.content
                sections = {
                    "Language Detected": "## Language Detected",
                    "Syntax Errors": "### Syntax Errors",
                    "Logical Issues/Bugs": "### Logical Issues/Bugs",
                    "Best Practices & Improvements": "### Best Practices & Improvements",
                    "Security & Performance Concerns": "### Security & Performance Concerns",
                    "Overall Suggestions": "### Overall Suggestions"
                }

                for section_name, header in sections.items():
                    if header in result_str:
                        start = result_str.find(header)
                        next_header = result_str.find("###", start + 1)
                        if next_header == -1:
                            next_header = len(result_str)
                        section_content = result_str[start:next_header].strip()
                        with st.expander(f"{section_name}"):
                            st.markdown(section_content)

                # Simple visualization: Extract confidence scores if present
                import re
                confidences = re.findall(r'(\w+ \w+ Confidence): (\d+)%', result_str)
                if confidences:
                    st.subheader("Confidence Scores Visualization")
                    categories = [cat for cat, score in confidences]
                    scores = [int(score) for cat, score in confidences]
                    st.bar_chart({cat: score for cat, score in zip(categories, scores)})
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
    else:
        st.warning("Please enter some code to analyze.")

st.sidebar.info("Powered by Groq and LangChain. Ensure your .env file has GROQ_API_KEY set.")
