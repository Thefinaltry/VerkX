import streamlit as st

# Define the pages for the Streamlit app
Pages = [st.Page("dashboard.py", title="Dashboard", icon="🏠"), 
         st.Page("docs.py", title="Docs", icon="📚")]


# Create the navigation menu
pg = st.navigation(Pages)

# Run the Streamlit app
pg.run()