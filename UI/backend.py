# To connect the functions in VerkX folder to the Streamlit app.
import sys
sys.path.append("..")  # Add the parent directory to the system path

# Import necessary modules from the backend
import streamlit as st
import get_data as gt
import efficient_frontier as ef
import rebalance as rb


def plot_efficient_frontier():

    period = str(f'{st.session_state.get("period")}y')
    interval = str(st.session_state.get("interval"))
    short_bound = st.session_state.get("short_position_limit")
    long_bound = st.session_state.get("long_position_limit")
    period_string = str(period)+'y'
    if st.session_state.data_source == "country":
        data = gt.get_data(country=st.session_state.get("country"), period=period, interval=interval)
    elif st.session_state.data_source == "custom ticker selection":
        data = gt.get_data(ticker=st.session_state.get("tickers"), period=period, interval=interval)
    returns,_ = gt.get_returns(data)
    print(returns)
    yearly_returns = gt.cal_yearly_returns(returns)
    if short_bound != None or long_bound != None:
        target_returns, stds, weights = ef.calculate_efficient_frontier(returns,yearly_returns,True,short_bound,long_bound)
    else:
        target_returns, stds, weights = ef.calculate_efficient_frontier(returns,yearly_returns,False)
    
    return target_returns, stds, weights

def calculate_minimum_variance_portfolio():
    pass