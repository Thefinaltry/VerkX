# To connect the functions in VerkX folder to the Streamlit app.
import sys
sys.path.append("..")  # Add the parent directory to the system path

# Import necessary modules from the backend
import streamlit as st
import get_data as gt
import efficient_frontier as ef
import rebalance as rb


def plot_efficient_frontier():
    '''
    This function retrieves the data based on the user's selection via the Streamlit interface,
    using session.state as a global variable to store the user's selections. It then calculates the 
    efficient frontier based on data retrived with yfinance in the functions from get_data.py and 
    efficient_frontier.py.

    input: None (but uses st.session_state to get user selections).
    output: target_returns, stds, weights (for the efficient frontier portfolios).
    Variables:
    - Period: str (e.g., '5y' for 5 years) P.S. Stores as int in session state for ef-period limits, converted in this function
    - Interval: str (e.g., '1d', '1mo', '1h', etc.)
    - Short position limit: float (e.g., 0.2 for 20%) or None
    - Long position limit: float (e.g., 0.2 for 20%) or None
    '''

    # data
    period = str(f'{st.session_state.get("period")}y')
    interval = str(st.session_state.get("interval"))
    short_bound = st.session_state.get("short_position_limit")
    long_bound = st.session_state.get("long_position_limit")

    # Retrieve data based on user selection
    if st.session_state.data_source == "country":
        data = gt.get_data(country=st.session_state.get("country"), period=period, interval=interval)
    elif st.session_state.data_source == "custom ticker selection":
        data = gt.get_data(ticker=st.session_state.get("tickers"), period=period, interval=interval)
    
    # Calculate returns and yearly returns
    returns,_ = gt.get_returns(data)
    yearly_returns = gt.cal_yearly_returns(returns)

    # Check if position size limits are selected and calculate the efficient frontier accordingly
    if short_bound != None or long_bound != None:
        target_returns, stds, weights = ef.calculate_efficient_frontier(returns,yearly_returns,True,short_bound,long_bound)
    else:
        target_returns, stds, weights = ef.calculate_efficient_frontier(returns,yearly_returns,False)
    

    return target_returns, stds, weights


def calculate_minimum_variance_portfolio():
    pass