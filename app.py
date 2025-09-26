import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
import difflib
from black import FileMode
import black
from main import create_analysis_chain
from utils import (
    flesch_kincaid_grade_level, cyclomatic_complexity, calculate_maintainability_index,
    lines_of_code, comment_lines, detect_code_smells, halstead_metrics
)
from chat import create_chat_chain, send_message

# Load environment variables
load_dotenv()

# Initialize analysis chain
chain = create_analysis_chain()

# Page configuration for professional look
st.set_page_config(
    page_title="AI Code Judge",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin-bottom: 1rem;
        color: #333;
    }
    .good-metric { border-left-color: #28a745; }
    .poor-metric { border-left-color: #dc3545; }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .footer {
        text-align: center;
        color: #666;
        margin-top: 2rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Session state for history and chat
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'chat_chain' not in st.session_state:
    st.session_state.chat_chain = None

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["Analyze & Input", "Format Code", "Chat", "History"])

# Main content
if page == "Analyze & Input":
    st.markdown('<div class="main-header">🤖 AI Code Judge</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Enter or upload code for a comprehensive AI-powered review. Supports multiple languages!</div>', unsafe_allow_html=True)

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

    if st.button("🔍 Analyze Code"):
        if code_input.strip():
            with st.spinner("Analyzing your code..."):
                try:
                    result = chain.invoke({"code": code_input})
                    st.success("Analysis Complete!")

                    # Calculate metrics
                    loc_dict = lines_of_code(code_input)
                    loc = loc_dict['value']
                    comments = comment_lines(code_input)
                    cc_dict = cyclomatic_complexity(code_input)
                    cc = cc_dict['value']
                    mi_dict = calculate_maintainability_index(code_input, loc, comments)
                    mi = mi_dict['value']
                    fkgl_dict = flesch_kincaid_grade_level(code_input)
                    fkgl = fkgl_dict['value']
                    smells = detect_code_smells(code_input)
                    halstead = halstead_metrics(code_input)

                    # Metrics dashboard
                    st.subheader("📊 Code Metrics Dashboard")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        status_class = "good-metric" if loc_dict['status'] == "good" else "poor-metric"
                        st.markdown(f'<div class="metric-card {status_class}"><strong>{loc_dict["label"]}</strong><br>{loc}</div>', unsafe_allow_html=True)
                    with col2:
                        status_class = "good-metric" if cc_dict['status'] == "good" else "poor-metric"
                        st.markdown(f'<div class="metric-card {status_class}"><strong>{cc_dict["label"]}</strong><br>{cc}</div>', unsafe_allow_html=True)
                    with col3:
                        status_class = "good-metric" if mi_dict['status'] == "good" else "poor-metric"
                        st.markdown(f'<div class="metric-card {status_class}"><strong>{mi_dict["label"]}</strong><br>{mi:.1f}%</div>', unsafe_allow_html=True)
                    with col4:
                        status_class = "good-metric" if fkgl_dict['status'] == "good" else "poor-metric"
                        st.markdown(f'<div class="metric-card {status_class}"><strong>{fkgl_dict["label"]}</strong><br>{fkgl:.1f}</div>', unsafe_allow_html=True)

                    # Halstead and smells
                    with st.expander("🔧 Detailed Metrics & Smells"):
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

                    # Analysis results in tabs
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Language", "Errors", "Best Practices", "Security", "Refactoring"])
                    result_str = result.content

                    def get_section(content, header):
                        start = content.find(header)
                        if start == -1:
                            return ""
                        next_header = content.find("###", start + 1)
                        if next_header == -1:
                            next_header = len(content)
                        return content[start:next_header].strip()

                    with tab1:
                        st.markdown(get_section(result_str, "### Language Detected"))
                    with tab2:
                        st.markdown(get_section(result_str, "### Syntax Errors"))
                        st.markdown(get_section(result_str, "### Logical Issues/Bugs"))
                    with tab3:
                        st.markdown(get_section(result_str, "### Best Practices & Improvements"))
                    with tab4:
                        st.markdown(get_section(result_str, "### Security & Performance Concerns"))
                    with tab5:
                        st.markdown(get_section(result_str, "### Refactoring Suggestions"))
                        st.markdown(get_section(result_str, "### Overall Suggestions"))

                    # Visualization
                    import re
                    confidences = re.findall(r'(\w+ \w+ Confidence): (\d+)%', result_str)
                    if confidences:
                        st.subheader("📈 Confidence Scores")
                        categories = [cat for cat, score in confidences]
                        scores = [int(score) for cat, score in confidences]
                        st.bar_chart({cat: score for cat, score in zip(categories, scores)})

                    # Add to history
                    st.session_state.analysis_history.append({
                        "code": code_input,
                        "result": result_str,
                        "metrics": {"loc": loc_dict, "cc": cc_dict, "mi": mi_dict, "fkgl": fkgl_dict}
                    })
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
        else:
            st.warning("Please enter some code to analyze.")

elif page == "Format Code":
    st.markdown('<div class="main-header">🛠️ Code Formatter</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Format your Python code using Black for consistent style.</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload a Python file", type=['py'])
    code_input = ""
    if uploaded_file is not None:
        code_input = uploaded_file.read().decode("utf-8")
        st.text_area("Uploaded code:", value=code_input, height=200, disabled=True)
    else:
        code_input = st.text_area(
            "Paste your Python code here:",
            placeholder="def example():\n    print('Hello')",
            height=200,
        )

    if st.button("🎨 Format Code") and code_input.strip():
        try:
            # Format the code using Black library
            try:
                formatted_code = black.format_file_contents(code_input, fast=False, mode=FileMode())
                if formatted_code == code_input:
                    st.success("Code is already formatted! ✅")
                else:
                    st.subheader("Formatting Changes:")
                    # Generate diff
                    diff = difflib.unified_diff(
                        code_input.splitlines(keepends=True),
                        formatted_code.splitlines(keepends=True),
                        fromfile='original.py',
                        tofile='formatted.py',
                    )
                    diff_text = ''.join(diff)
                    if diff_text.strip():
                        st.code(diff_text, language=None)
                    else:
                        st.info("No changes detected.")
                    
                    if st.button("Apply Formatting"):
                        st.text_area("Formatted code:", value=formatted_code, height=200)
            except Exception as black_error:
                st.error(f"Black formatting error: {black_error}")
        except Exception as e:
            st.error(f"Formatting failed: {e}")

elif page == "Chat":
    st.markdown('<div class="main-header">💬 Chat about Code</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Discuss your code with the AI assistant.</div>', unsafe_allow_html=True)

    if st.session_state.chat_chain is None:
        if st.button("🚀 Start Chat"):
            st.session_state.chat_chain = create_chat_chain()
            st.success("Chat initialized!")
            st.rerun()
    if st.session_state.chat_chain:
        chat_input = st.text_input("Ask about your code:")
        if st.button("📤 Send Message") and chat_input.strip():
            response = send_message(st.session_state.chat_chain, chat_input)
            st.markdown(f"**You:** {chat_input}")
            st.markdown(f"**AI:** {response}")

elif page == "History":
    st.markdown('<div class="main-header">📚 Analysis History</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Review your previous code analyses.</div>', unsafe_allow_html=True)

    if st.session_state.analysis_history:
        for i, entry in enumerate(st.session_state.analysis_history):
            loc_val = entry['metrics']['loc']['value']
            cc_val = entry['metrics']['cc']['value']
            mi_val = entry['metrics']['mi']['value']
            fkgl_val = entry['metrics']['fkgl']['value']
            with st.expander(f"Analysis {i+1} - LOC: {loc_val}, CC: {cc_val}"):
                st.code(entry["code"][:500] + "..." if len(entry["code"]) > 500 else entry["code"])
                st.markdown(f"**Metrics:** MI: {mi_val:.1f}%, Readability: {fkgl_val:.1f}")
    else:
        st.info("No history yet. Analyze some code to see it here.")

# Footer
st.markdown('<div class="footer">Powered by Groq and LangChain. Version 1.0.0</div>', unsafe_allow_html=True)
