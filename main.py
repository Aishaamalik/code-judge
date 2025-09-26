import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import subprocess
import tempfile
import os
import sys
sys.path.append('.')
from utils import (
    flesch_kincaid_grade_level, cyclomatic_complexity, calculate_maintainability_index,
    lines_of_code, comment_lines, detect_code_smells, halstead_metrics
)
from chat import create_chat_chain, send_message

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

# Prompt template for enhanced code review with metrics, smells, and refactoring
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
3. Structure your response with clear sections using Markdown formatting, emojis for visual appeal (✅ for no issues, ⚠️ for warnings, 🔴 for errors), bullet points, and tables where appropriate (e.g., for issues, metrics, and recommendations). Use headings like ## Language Detected, ### Syntax Errors, etc.
   - Language Detected: Include confidence score.
   - Syntax Errors: (List if any with 🔴, else "None detected" with ✅)
   - Logical Issues/Bugs: (List if any with ⚠️ or 🔴, else "None detected" with ✅)
   - Code Smells: (List if any with ⚠️, else "None detected" with ✅)
   - Best Practices & Improvements: Bullet points with suggestions.
   - Security & Performance Concerns: Highlight with emojis.
   - Code Metrics: Table or bullets with estimated values and interpretations (e.g., Cyclomatic Complexity: 5 (Low - Good)).
   - Refactoring Suggestions: Detailed ideas with code examples in ``` blocks.
   - Overall Suggestions: Include refactored code in ``` blocks if relevant.
4. Provide confidence scores (0-100%) for each major section, e.g., "Syntax Analysis Confidence: 95%". Base scores on how clear the code is and your certainty. Suggest key metrics for visualization if possible (e.g., complexity score, maintainability).

Code to analyze:
{code}

Respond in a helpful, professional tone. Be thorough, detailed, and concise, focusing on visual structure for better readability. Prioritize actionable insights.
"""

prompt = PromptTemplate(
    input_variables=["code"],
    template=prompt_template,
)

# Create LLM chain
chain = prompt | llm

# Session state for history and chat
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'chat_chain' not in st.session_state:
    st.session_state.chat_chain = None

# Streamlit UI
st.title("🤖 AI Code Judge")
st.write("Enter or upload code for a comprehensive AI-powered review. Supports multiple languages!")

# File upload
uploaded_file = st.file_uploader("Upload a code file", type=['py', 'js', 'java', 'cpp', 'c', 'txt'])
code_input = ""
if uploaded_file is not None:
    code_input = uploaded_file.read().decode("utf-8")
    st.text_area("Uploaded code:", value=code_input, height=200, disabled=True)
else:
    code_input = st.text_area(
        "Or paste your code here:",
        placeholder="""# Example Python code
def hello_world():
    print("Hello, World!")""",
        height=200,
    )

col1, col2 = st.columns(2)
with col1:
    analyze_button = st.button("Analyze Code", type="primary")
with col2:
    format_button = st.button("Format Code with Black")

if format_button and code_input.strip():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code_input)
        temp_file = f.name
    try:
        result = subprocess.run(['black', '--diff', temp_file], capture_output=True, text=True)
        if result.returncode == 0:
            st.success("Code is already formatted!")
        else:
            st.subheader("Formatting Diff:")
            st.code(result.stdout, language='diff')
            if st.button("Apply Formatting"):
                subprocess.run(['black', temp_file])
                with open(temp_file, 'r') as f:
                    formatted_code = f.read()
                st.text_area("Formatted code:", value=formatted_code, height=200)
    except Exception as e:
        st.error(f"Formatting failed: {e}")
    finally:
        os.unlink(temp_file)

if analyze_button:
    if code_input.strip():
        with st.spinner("Analyzing your code..."):
            try:
                result = chain.invoke({"code": code_input})
                st.subheader("Analysis Results:")

                # Calculate metrics
                loc = lines_of_code(code_input)
                comments = comment_lines(code_input)
                cc = cyclomatic_complexity(code_input)
                mi = calculate_maintainability_index(code_input, loc, comments)
                fkgl = flesch_kincaid_grade_level(code_input)
                smells = detect_code_smells(code_input)
                halstead = halstead_metrics(code_input)

                # Display metrics in expander
                with st.expander("📊 Code Metrics"):
                    st.markdown(f"**Lines of Code:** {loc}")
                    st.markdown(f"**Comment Lines:** {comments}")
                    st.markdown(f"**Cyclomatic Complexity:** {cc} ({'Low' if cc <= 10 else 'High'})")
                    st.markdown(f"**Maintainability Index:** {mi:.2f}% ({'Good' if mi > 50 else 'Poor'})")
                    st.markdown(f"**Readability (Flesch-Kincaid Grade Level):** {fkgl:.2f} ({'Easy' if fkgl < 8 else 'Hard'})")
                    st.markdown("**Halstead Metrics:**")
                    st.markdown(f"- Vocabulary: {halstead['vocabulary']}")
                    st.markdown(f"- Volume: {halstead['volume']:.2f}")
                    st.markdown(f"- Difficulty: {halstead['difficulty']:.2f}")
                    st.markdown(f"- Effort: {halstead['effort']:.2f}")
                    if smells:
                        st.markdown("**Code Smells Detected:**")
                        for smell in smells:
                            st.markdown(f"- ⚠️ {smell}")
                    else:
                        st.markdown("**Code Smells:** None detected ✅")

                # Parse and display sections in collapsible expanders for better organization
                result_str = result.content
                sections = {
                    "Language Detected": "## Language Detected",
                    "Syntax Errors": "### Syntax Errors",
                    "Logical Issues/Bugs": "### Logical Issues/Bugs",
                    "Code Smells": "### Code Smells",
                    "Best Practices & Improvements": "### Best Practices & Improvements",
                    "Security & Performance Concerns": "### Security & Performance Concerns",
                    "Code Metrics": "### Code Metrics",
                    "Refactoring Suggestions": "### Refactoring Suggestions",
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

                # Add to history
                st.session_state.analysis_history.append({
                    "code": code_input,
                    "result": result_str,
                    "metrics": {"loc": loc, "cc": cc, "mi": mi, "fkgl": fkgl}
                })
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
    else:
        st.warning("Please enter some code to analyze.")

# Chat expander
with st.expander("💬 Chat about Code"):
    if st.session_state.chat_chain is None:
        if st.button("Start Chat"):
            st.session_state.chat_chain = create_chat_chain()
            st.success("Chat initialized!")
    if st.session_state.chat_chain:
        chat_input = st.text_input("Ask about your code:")
        if st.button("Send Message"):
            if chat_input.strip():
                response = send_message(st.session_state.chat_chain, chat_input)
                st.write(f"**You:** {chat_input}")
                st.write(f"**AI:** {response}")

# History expander
with st.expander("📚 Analysis History"):
    if st.session_state.analysis_history:
        for i, entry in enumerate(st.session_state.analysis_history):
            st.markdown(f"**Analysis {i+1}:**")
            st.code(entry["code"][:100] + "..." if len(entry["code"]) > 100 else entry["code"])
            st.markdown(f"LOC: {entry['metrics']['loc']}, CC: {entry['metrics']['cc']}, MI: {entry['metrics']['mi']:.1f}%")
    else:
        st.write("No history yet.")

st.sidebar.info("Powered by Groq and LangChain. Ensure your .env file has GROQ_API_KEY set.")
