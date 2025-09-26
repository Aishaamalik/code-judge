# TODO List for Professional UI/UX Redo of AI Code Judge App

## Phase 1: Preparation and Dependencies
- [ ] Review and update requirements.txt (add streamlit-extras for advanced components like tabs if needed)
- [ ] Enhance utils.py: Modify metric functions to return formatted data (e.g., dicts with labels, colors, thresholds) for easier UI integration

## Phase 2: Core UI/UX Overhaul in main.py
- [ ] Add st.set_page_config for wide layout, custom favicon, and initial theme setup
- [ ] Restructure overall layout: Implement sidebar navigation with tabs (Analyze, Format, Chat, History) instead of expanders for better flow
- [ ] Enhance header: Professional title with emoji, subtitle, and hero section (brief value proposition)
- [ ] Improve input section: Styled file upload with preview, enhanced text area with better placeholders, buttons in columns with icons
- [ ] Redesign analysis display: Use containers for sections, styled elements (success/warning boxes for issues), interactive charts (bar for metrics, pie for smells)
- [ ] Create metrics dashboard: Grid layout with KPI cards (colored based on good/poor thresholds: green/red)
- [ ] Integrate chat/history: As sidebar tabs with message bubbles for chat and collapsible history items
- [ ] Add professional error handling: Toasts/notifications instead of basic st.error
- [ ] Inject custom CSS: For buttons, spacing, fonts, and consistent branding (tech theme: blues/grays, primary #1f77b4, secondary #ff7f0e)
- [ ] Add footer: Version info and powered-by credits

## Phase 3: Testing and Refinement
- [ ] Run the app locally (streamlit run main.py) and verify all features work (analyze, format, chat, history)
- [ ] Test responsiveness on different screen sizes/devices
- [ ] Debug any issues (e.g., theme conflicts, session state problems)
- [ ] Gather feedback and iterate on UI elements if needed

## Phase 4: Documentation and Finalization
- [ ] Update README.md with UI screenshots, deployment notes, and feature highlights
- [ ] Mark all tasks complete and archive old TODO items
