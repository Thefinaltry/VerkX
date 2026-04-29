import streamlit as st

# initializing page 
st.markdown("# Data Selection")
st.sidebar.markdown("# Data Selection")

# Page description
st.write("""
        SETJA EH FLOTT HÉR!!!!!
        """)

# Data source selection
data_source = st.selectbox("Select a data source", options=["country", "custom ticker selection"])
st.session_state.data_source = data_source
if data_source == "country":
    st.title(
        "Country Selection. Note: Only Icelandic data is supported as of now."
        )
    country = st.selectbox("Select a country", options=["ICELAND", "USA", "CANADA", "GERMANY", "FRANCE"])
    st.session_state["country"] = country
else:
    st.title("Custom Ticker Selection")
    tickers_input = st.text_input(
        "Enter ticker symbols separated by commas (e.g., AAPL, MSFT, GOOGL). Note: Only Icelandic tickers are supported as of now."
        )
    tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]
    st.session_state["tickers"] = tickers

# Period selection
st.session_state["period"] = st.number_input("Select the period for data retrieval in years:", min_value=1, max_value=10, step=1)

# Interval selection
interval_data_type = st.selectbox("Select the data interval", options=["days", "hours", "minutes"])
if interval_data_type == "days":
    interval_value = st.number_input('Select the number of days for data retrieval:', min_value=1, max_value=365, step=1)
    st.session_state["interval"] = f"{interval_value}d"
elif interval_data_type == "hours":
    interval_value = st.number_input('Select the number of hours for data retrieval:', min_value=1, max_value=24*365, step=1)
    st.session_state["interval"] = f"{interval_value}h"
else:
    interval_value = st.number_input('Select the number of minutes for data retrieval:', min_value=1, max_value=60*24*365, step=1)
    st.session_state["interval"] = f"{interval_value}m"

# Efficient frontier period selection
select_ef_period = st.checkbox("select how many years of data to calculate the efficient frontier", value=False)
if select_ef_period:
    st.session_state["ef_period"] = st.number_input("Years to calculate the efficient frontier:", min_value=1, max_value=st.session_state["period"]-1, step=1)

# Rebalancing strategy selection
select_rebalace_strategy = st.checkbox("Select a rebalancing strategy", value=False)
if select_rebalace_strategy:

    # Risk-based rebalancing strategy
    Risk_based_rebalance = st.checkbox("Risk-based rebalancing strategy", value=False)
    if Risk_based_rebalance:
        st.session_state["risk-level"] = st.number_input("Select a risk level", min_value=0, max_value=10, step=1)
    
    # Slope-based rebalancing strategy
    slope_based_rebalance = st.checkbox("Slope-based rebalancing strategy", value=False)
    if slope_based_rebalance:
        st.session_state["slope"] = True
    
    # Drift-based rebalancing strategy
    drift_based_rebalance = st.checkbox("Drift-based rebalancing strategy", value=False)
    if drift_based_rebalance:
        st.session_state["drift-margine"] = st.number_input("Select a drift margine (e.g., 0.05 for 5%)", min_value=0.0, max_value=1.0, step=0.01)
    
    # Rebalancing period selection
    rebalance_period = st.number_input("Select the rebalancing period in days:", min_value=1, max_value=365, step=1)
    st.session_state["rebalance_period"] = rebalance_period

    # Position size limits selection
    select_limits = st.checkbox("Select limits position size", value=False)
    if select_limits:
        st.session_state["long_position_limit"] = st.number_input("Select the maximum long-position size as a percentage of the portfolio (e.g., 0.2 for 20%)", min_value=0.0, max_value=1.0, step=0.01)
        st.session_state["short_position_limit"] = st.number_input("Select the maximum short-position size as a percentage of the portfolio (e.g., 0.2 for 20%)", min_value=0.0, max_value=1.0, step=0.01)
    else:
        st.session_state["long_position_limit"] = None
        st.session_state["short_position_limit"] = None
