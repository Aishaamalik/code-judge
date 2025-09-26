import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
import difflib
from black import FileMode
import black
from groq import APIStatusError
from main import create_analysis_chain, create_multi_file_analysis_chain
from utils import (
    flesch_kincaid_grade_level, cyclomatic_complexity, calculate_maintainability_index,
    lines_of_code, comment_lines, detect_code_smells, halstead_metrics,
    nesting_depth, function_count, variable_count, code_duplication_percentage,
    code_characters, code_comment_density, code_avg_function_length
)
from chat import create_chat_chain, send_message
from analysis_export import export_to_pdf, export_to_json
from code_comparison import compare_codes
from github import Github

# Load environment variables
load_dotenv()



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

# Session state for history, chat, and settings
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'chat_chain' not in st.session_state:
    st.session_state.chat_chain = None
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.1

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["Analyze & Input", "Format Code", "Chat", "History", "Code Comparison", "Multi-File Analysis", "GitHub Repo", "Settings"])

# Main content
if page == "Analyze & Input":
    st.markdown('<div class="main-header">🤖 AI Code Judge</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Enter or upload code for a comprehensive AI-powered review. Supports AI-powered analysis for multiple programming languages; static metrics are estimates across languages.</div>', unsafe_allow_html=True)

    # File upload
    uploaded_file = st.file_uploader("Upload a code file", type=['py', 'js', 'java', 'cpp', 'c', 'txt', 'rs', 'go', 'php', 'rb', 'swift', 'kt', 'ts', 'html', 'css', 'json', 'xml'])
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
                    chain = create_analysis_chain(temperature=st.session_state.temperature)
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
                    nd_dict = nesting_depth(code_input)
                    nd = nd_dict['value']
                    fc_dict = function_count(code_input)
                    fc = fc_dict['value']
                    vc_dict = variable_count(code_input)
                    vc = vc_dict['value']
                    dup_dict = code_duplication_percentage(code_input)
                    dup = dup_dict['value']
                    chars_dict = code_characters(code_input)
                    cd_dict = code_comment_density(code_input)
                    afl_dict = code_avg_function_length(code_input)
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
                        st.markdown("**Code Dimensions:**")
                        st.markdown(f"- {chars_dict['label']}: {chars_dict['value']}")
                        st.markdown(f"- {cd_dict['label']}: {cd_dict['value']:.1f}%")
                        st.markdown(f"- {afl_dict['label']}: {afl_dict['value']:.1f}")
                        if smells:
                            st.markdown("**Code Smells Detected:**")
                            for smell in smells:
                                st.markdown(f"- ⚠️ {smell}")
                        else:
                            st.markdown("**Code Smells:** None detected ✅")

                    # Analysis results in tabs
                    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(["Language", "Errors", "Best Practices", "Security", "Metrics", "Dependency", "Test Coverage", "Complexity", "Duplication", "Refactoring"])
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
                        st.markdown(get_section(result_str, "### Code Metrics"))
                    with tab6:
                        st.markdown(get_section(result_str, "### Dependency Analysis"))
                    with tab7:
                        st.markdown(get_section(result_str, "### Test Coverage Estimation"))
                    with tab8:
                        st.markdown(get_section(result_str, "### Time/Space Complexity Estimation"))
                    with tab9:
                        st.markdown(get_section(result_str, "### Code Duplication Detection"))
                    with tab10:
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

                    # Export options
                    st.subheader("📤 Export Analysis")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Export to PDF"):
                            export_to_pdf(result_str, {"loc": loc_dict, "cc": cc_dict, "mi": mi_dict, "fkgl": fkgl_dict, "nd": nd_dict, "fc": fc_dict, "vc": vc_dict, "dup": dup_dict, "chars": chars_dict, "cd": cd_dict, "afl": afl_dict}, "analysis_report.pdf")
                            st.success("PDF exported!")
                    with col2:
                        if st.button("Export to JSON"):
                            export_to_json(result_str, {"loc": loc_dict, "cc": cc_dict, "mi": mi_dict, "fkgl": fkgl_dict, "nd": nd_dict, "fc": fc_dict, "vc": vc_dict, "dup": dup_dict, "chars": chars_dict, "cd": cd_dict, "afl": afl_dict}, "analysis_report.json")
                            st.success("JSON exported!")

                    # Add to history
                    st.session_state.analysis_history.append({
                        "code": code_input,
                        "result": result_str,
                        "metrics": {"loc": loc_dict, "cc": cc_dict, "mi": mi_dict, "fkgl": fkgl_dict, "nd": nd_dict, "fc": fc_dict, "vc": vc_dict, "dup": dup_dict, "chars": chars_dict, "cd": cd_dict, "afl": afl_dict}
                    })
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
        else:
            st.warning("Please enter some code to analyze.")

elif page == "Format Code":
    st.markdown('<div class="main-header">🛠️ Code Formatter</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Format your Python code using Black for consistent style. Note: This feature is Python-specific. For other languages, use dedicated tools like Prettier (JS), clang-format (C++), etc.</div>', unsafe_allow_html=True)
    st.warning("⚠️ Code formatting is currently available only for Python. Upload or paste Python code below.")

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
            st.session_state.chat_chain = create_chat_chain(temperature=st.session_state.temperature)
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

elif page == "Code Comparison":
    st.markdown('<div class="main-header">🔄 Code Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Compare two code snippets side-by-side.</div>', unsafe_allow_html=True)

    code1 = st.text_area("Code 1", height=200)
    code2 = st.text_area("Code 2", height=200)

    if st.button("Compare"):
        if code1.strip() and code2.strip():
            comp = compare_codes(code1, code2)
            st.subheader("Diff")
            st.code(comp['diff'])
            st.subheader("Metrics Comparison")
            import pandas as pd
            data = []
            for key in comp['metrics1']:
                data.append({
                    "Metric": comp['metrics1'][key]['label'],
                    "Code 1": comp['metrics1'][key]['value'],
                    "Code 2": comp['metrics2'][key]['value'],
                    "Comparison": comp['comparison'][key]
                })
            df = pd.DataFrame(data)
            st.table(df)
        else:
            st.warning("Please enter both code snippets.")

elif page == "Multi-File Analysis":
    st.markdown('<div class="main-header">📁 Multi-File Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload multiple files for project-level analysis.</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Upload multiple files", accept_multiple_files=True)

    if uploaded_files:
        st.write(f"Uploaded {len(uploaded_files)} files.")

        if st.button("Analyze All"):
            all_results = []

            # Loop through each file and perform detailed analysis
            for file in uploaded_files:
                code = file.read().decode("utf-8")
                original_len = len(code)
                if len(code) > 8000:
                    code = code[:8000]
                    st.warning(f"File {file.name} is too large ({original_len} characters). Analyzing only the first 8000 characters.")

                # Escape curly braces in code to prevent them from being interpreted as template variables
                escaped_code = code.replace('{', '{{').replace('}', '}}')

                try:
                    # Construct the prompt for detailed analysis
                    prompt = f"""
                    Please analyze the following Python code in detail. Provide the following insights:
                    1. A general overview of the code structure (modularity, readability, and maintainability).
                    2. Identify the cyclomatic complexity and potential areas for refactoring.
                    3. Check for any coding best practices violations (e.g., long functions, deep nesting, code duplication).
                    4. Highlight any code smells, such as repeated patterns, overly complex logic, or inefficient code.
                    5. Assess performance implications (e.g., unnecessary computations, inefficient algorithms).

                    If any issues are found, suggest improvements where applicable.

                    Code:
                    {escaped_code}
                    """

                    # Invoke multi-chain analysis with the constructed prompt
                    multi_chain = create_multi_file_analysis_chain(custom_prompt=prompt, temperature=st.session_state.temperature)
                    result = multi_chain.invoke({"code": code})

                    # Collect detailed metrics
                    loc = lines_of_code(code)['value']
                    cc = cyclomatic_complexity(code)['value']
                    comments = comment_lines(code)
                    mi = calculate_maintainability_index(code, loc, comments)['value']  # Maintainability Index
                    halstead = halstead_metrics(code)  # Halstead metrics
                    nesting_depth_val = nesting_depth(code)['value']  # Nesting depth
                    code_smells_list = detect_code_smells(code)  # Code smells

                    # Append results for each file
                    all_results.append({
                        "file": file.name,
                        "loc": loc,
                        "cc": cc,
                        "mi": mi,
                        "halstead": halstead,
                        "nesting_depth": nesting_depth_val,
                        "code_smells": code_smells_list,
                        "result": result.content
                    })

                except APIStatusError as e:
                    st.error(f"Analysis failed for {file.name}: {str(e)}")
                    continue

            # Display summary of results
            st.subheader("Summary")
            for res in all_results:
                st.write(f"**{res['file']}**: LOC {res['loc']}, CC {res['cc']}, MI {res['mi']}")
                st.write(f"Halstead Metrics: {res['halstead']}")
                st.write(f"Nesting Depth: {res['nesting_depth']}")
                st.write(f"Code Smells Detected: {len(res['code_smells'])}")
                st.text_area(f"Detailed Analysis for {res['file']}", res['result'], height=200)

                # Optionally, visualize the metrics
                st.bar_chart({
                    'LOC': res['loc'],
                    'CC': res['cc'],
                    'MI': res['mi'],
                    'Nesting Depth': res['nesting_depth']
                })

                # Show a list of detected code smells
                if res['code_smells']:
                    st.write("Potential Code Smells:")
                    for smell in res['code_smells']:
                        st.write(f"- {smell}")

elif page == "GitHub Repo":
    st.markdown('<div class="main-header">🐙 GitHub Repo Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Analyze a GitHub repository by URL.</div>', unsafe_allow_html=True)

    repo_url = st.text_input("GitHub Repo URL")
    if st.button("Analyze Repo"):
        if repo_url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(repo_url)
                path = parsed.path.strip('/')
                if '/' not in path:
                    st.error("Invalid GitHub URL. Please provide a URL like https://github.com/owner/repo")
                else:
                    owner, repo = path.split('/', 1)
                    if '/' in repo:
                        repo = repo.split('/')[0]  # in case of subpaths
                    g = Github()
                    repo_obj = g.get_repo(f"{owner}/{repo}")
                    st.success(f"Analyzing repo: {repo_obj.full_name}")

                    # Get contents of root directory
                    contents = repo_obj.get_contents("")
                    code_files = []
                    for content in contents:
                        if content.type == "file" and any(content.name.endswith(ext) for ext in ['.py', '.js', '.java', '.cpp', '.c', '.rs', '.go', '.php', '.rb', '.swift', '.kt', '.ts', '.html', '.css', '.json', '.xml']):
                            code_files.append(content)

                    if not code_files:
                        st.warning("No code files found in the root directory.")
                    else:
                        st.write(f"Found {len(code_files)} code files. Analyzing up to 5 files.")

                        # Analyze up to 5 files
                        for i, file in enumerate(code_files[:5]):
                            with st.expander(f"Analysis of {file.name}"):
                                try:
                                    code = file.decoded_content.decode('utf-8')
                                    original_len = len(code)
                                    if len(code) > 8000:
                                        code = code[:8000]
                                        st.warning(f"File {file.name} is too large ({original_len} characters). Analyzing only the first 8000 characters.")

                                    # Calculate metrics
                                    loc_dict = lines_of_code(code)
                                    loc = loc_dict['value']
                                    comments = comment_lines(code)
                                    cc_dict = cyclomatic_complexity(code)
                                    cc = cc_dict['value']
                                    mi_dict = calculate_maintainability_index(code, loc, comments)
                                    mi = mi_dict['value']
                                    fkgl_dict = flesch_kincaid_grade_level(code)
                                    fkgl = fkgl_dict['value']
                                    smells = detect_code_smells(code)
                                    halstead = halstead_metrics(code)

                                    # Metrics display
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

                                    # AI Analysis
                                    chain = create_analysis_chain(temperature=st.session_state.temperature)
                                    result = chain.invoke({"code": code})
                                    result_str = result.content

                                    # Display sections
                                    def get_section(content, header):
                                        start = content.find(header)
                                        if start == -1:
                                            return ""
                                        next_header = content.find("###", start + 1)
                                        if next_header == -1:
                                            next_header = len(content)
                                        return content[start:next_header].strip()

                                    st.markdown(get_section(result_str, "### Language Detected"))
                                    st.markdown(get_section(result_str, "### Syntax Errors"))
                                    st.markdown(get_section(result_str, "### Logical Issues/Bugs"))
                                    st.markdown(get_section(result_str, "### Best Practices & Improvements"))
                                    st.markdown(get_section(result_str, "### Security & Performance Concerns"))
                                    st.markdown(get_section(result_str, "### Code Metrics"))
                                    st.markdown(get_section(result_str, "### Refactoring Suggestions"))

                                except Exception as e:
                                    st.error(f"Failed to analyze {file.name}: {str(e)}")

            except Exception as e:
                st.error(f"Error accessing repository: {str(e)}")
        else:
            st.warning("Please enter a GitHub URL.")

elif page == "Settings":
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Adjust AI parameters.</div>', unsafe_allow_html=True)

    st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, st.session_state.temperature)
    st.write(f"Current temperature: {st.session_state.temperature}")
    st.info("Changes will apply on next analysis.")

# Footer
st.markdown('<div class="footer">Powered by Groq and LangChain. Version 1.0.0</div>', unsafe_allow_html=True)
