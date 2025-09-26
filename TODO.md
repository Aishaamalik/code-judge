# TODO: Add More Features and Deepen Code Analysis

## Steps to Complete:

1. **Deepen Code Analysis in main.py**
   - Update the prompt template to include new sections: Dependency Analysis, Test Coverage Estimation, Time/Space Complexity Estimation, Code Duplication Detection.
   - Add confidence scores for new sections.

2. **Add More Metrics in utils.py**
   - Implement nesting depth calculation.
   - Implement function/method count.
   - Implement variable count.
   - Implement code duplication percentage (simple heuristic).

3. **Create New Files**
   - Create analysis_export.py for PDF and JSON export functionality.
   - Create code_comparison.py for code comparison logic.

4. **Update app.py for New Features**
   - Add Code Comparison page.
   - Add Export Analysis functionality.
   - Add Multi-File Analysis page.
   - Add GitHub Repo Analysis page.
   - Add Settings page for LLM parameters.
   - Enhance Visualizations: Radar chart, pie chart for smells.
   - Improve Chat with analysis context.
   - Update sidebar navigation and UI components.

5. **Enhance chat.py**
   - Modify conversation chain to include recent analysis context.

6. **Update requirements.txt**
   - Add new dependencies: reportlab, requests, PyGithub.

7. **Update README.md**
   - Document new features and usage instructions.

8. **Testing and Verification**
   - Install dependencies and run app locally.
   - Test new features on sample code from different languages.
   - Verify exports, comparisons, and multi-file analysis.
   - Update this TODO.md as steps complete.

Progress: Step 1 completed - Deepened code analysis in main.py.
Step 2 completed - Added more metrics in utils.py.
Step 3 completed - Created new files analysis_export.py and code_comparison.py.
Step 4 completed - Updated app.py for new features.
Step 6 completed - Updated requirements.txt with pandas and reportlab.
