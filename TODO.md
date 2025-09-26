# TODO: Make GitHub Repo and Settings Pages Functional

## Steps to Complete
- [x] Edit requirements.txt: Add 'PyGithub==2.4.0' for GitHub API access.
- [x] Edit main.py: Add temperature parameter (default 0.1) to create_analysis_chain, create_multi_file_analysis_chain, and create_chat_chain; pass temperature to LLM in chain setup.
- [x] Edit app.py: 
  - [x] Initialize st.session_state.temperature = 0.1 if not present.
  - [x] Update Settings page to set st.session_state.temperature from slider.
  - [x] Move chain creations to use st.session_state.temperature dynamically.
  - [x] Implement GitHub Repo page: Parse URL, fetch repo contents using PyGithub, filter code files, analyze each with metrics and AI chain, display results in expanders.
- [x] Install new dependency: Run 'pip install -r requirements.txt'.
- [ ] Test the app: Run 'streamlit run app.py', adjust settings, test analysis, and GitHub repo analysis with a sample URL.
