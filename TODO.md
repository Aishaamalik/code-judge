# TODO: Add Code Dimensions to Analysis

## Steps to Complete

- [x] Add new metric functions to utils.py: code_characters, code_comment_density, code_avg_function_length
- [x] Update main.py: Modify the prompt template to include new metrics (code characters, comment density, avg lines per function) in the instructions
- [ ] Update app.py (Analyze & Input): Import new functions, calculate metrics, add to detailed metrics expander, include in export dict
- [ ] Update app.py (Multi-File Analysis): Calculate and display new metrics for each file
- [ ] Update app.py (GitHub Repo): Calculate and display new metrics for analyzed files
- [ ] Update code_comparison.py: Add new metrics to the metrics comparison
- [ ] Test the implementation: Run the app and verify new metrics are displayed and exported correctly
