import streamlit as st
import functions as f

# initializing page 
st.markdown("# Data Selection")
st.sidebar.markdown("# Data Selection")

# Page description
st.write("""
        SETJA EH FLOTT HÉR!!!!!
        """)


# Data source selection
data_source = st.selectbox("Select a data source", options=["country", "custom ticker selection"])
if data_source == "country":
    st.title(
        "Country Selection. Note: Only Icelandic data is supported as of now."
        )
    country = st.selectbox("Select a country", options=["ICELAND", "USA", "CANADA", "GERMANY", "FRANCE"])
else:
    st.title("Custom Ticker Selection")
    tickers_input = st.text_input(
        "Enter ticker symbols separated by commas (e.g., AAPL, MSFT, GOOGL). Note: Only Icelandic tickers are supported as of now."
        )
    tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]


# Period selection
period = st.number_input("Select the period for data retrieval in years:", 
                        # Limits
                        min_value=2, max_value=20, step=1)

ef_period = st.number_input("Select the period for efficient frontier calculation in years:",
                        # Limits
                        min_value=1, max_value=period-1, step=1)

# Rebalancing period selection
rebalance_period = st.number_input("Select the rebalancing period in days:", min_value=1, max_value=365, step=1)

# Save Button to trigger data retrieval and processing
save_button = st.button("Save Selections")
if save_button:

    data = f.get_data(
            ticker=tickers if data_source == "custom ticker selection" else None, 
            country=country if data_source == "country" else None, 
            period=str(f'{period}y'))
    
    returns, ef_returns = f.get_returns(
                            data = data,
                            slice_output = True, 
                            ef_period = ef_period)
    
    st.session_state.update({
        "data": data,
        "returns": returns,
        "ef_returns": ef_returns
    })      

    st.session_state.update({
        "data_source": data_source,
        "country": country if data_source == "country" else None,
        "tickers": tickers if data_source == "custom ticker selection" else None,
        "period": period,
        "ef_period": ef_period,
        "frequency": rebalance_period,
        "data_selected": True,
        "yearly_returns": f.cal_yearly_returns(st.session_state["returns"])
    })
    f.efficient_frontier_and_min_var_data()

    st.switch_page("optimization.py")

    
else: 
    st.warning("Please make your selections and click 'Save Selections' to proceed.")
    st.session_state["data_selected"] = False
