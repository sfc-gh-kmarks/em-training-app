import streamlit as st

st.set_page_config(
    page_title="EM Training Assessment",
    page_icon=":material/school:",
    layout="wide",
)

page = st.navigation(
    {
        "Training": [
            st.Page("app_pages/simulation.py", title="Simulation Assessment", icon=":material/quiz:"),
            st.Page("app_pages/case_studies.py", title="Case Studies", icon=":material/menu_book:"),
        ],
        "Severity": [
            st.Page("app_pages/severity_decision_tree.py", title="Decision Tree", icon=":material/account_tree:"),
            st.Page("app_pages/practice_cases.py", title="Practice Cases", icon=":material/school:"),
        ],
    },
    position="sidebar",
)

st.sidebar.header(":material/school: EM Training")
st.sidebar.caption("Escalation Manager Training & Reference")

page.run()
