# TODO: Make Project Language-Agnostic

## Steps to Complete:

1. **Generalize metrics in utils.py**
   - Expand comment detection to more language styles (e.g., add SQL --, Haskell ', etc.).
   - Broaden cyclomatic complexity keywords to include more control flow structures across languages (e.g., add 'switch', 'match', 'try-except/try-catch').
   - Generalize code smells detection (e.g., detect common debug patterns like console.log, System.out, etc., instead of just print).
   - Ensure other metrics remain neutral.

2. **Update app.py for multi-language enhancements**
   - Broaden file uploader to include more extensions (e.g., .rs for Rust, .go for Go, .php, .rb, .swift, .kt, etc.).
   - In "Format Code" section: Add a warning/note that formatting is Python-only; disable or hide for non-Python files.
   - Update sub-header to clarify: "Supports AI-powered analysis for multiple programming languages; static metrics are estimates across languages."

3. **Update README.md**
   - Add section on language support: Explain AI-driven analysis for any language via LLM, with static metrics generalized but approximate for non-Python code.
   - Mention supported upload extensions and limitations (e.g., formatting is Python-specific).

4. **Testing and Verification**
   - Run the app locally (if needed, via streamlit run app.py).
   - Test analysis on sample code from different languages (Python, JS, Rust, etc.).
   - Verify metrics and formatting behavior.
   - Update this TODO.md as steps complete.

Progress: Step 1 completed - Generalized metrics in utils.py.
Step 2 completed - Updated app.py for multi-language enhancements.
Step 3 completed - Updated README.md with language support details.
