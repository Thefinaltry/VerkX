import streamlit as st

# Define the pages for the Streamlit app
Pages = [st.Page("home.py", title="Home", icon="🏠"), st.Page("data_selection.py", title="Data Selection", icon="📊"), 
         st.Page("optimization.py", title="Optimization", icon="⚙️"), st.Page("results.py", title="Results", icon="📈"), 
         st.Page("about.py", title="About", icon="ℹ️")]


# Create the navigation menu
pg = st.navigation(Pages)

# Run the Streamlit app
pg.run()