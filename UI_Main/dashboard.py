import streamlit as st
import pandas as pd
import numpy as np
import backend as bk
import texts as tx
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="Optimization Dashboard", layout="wide")


def init_state():
    defaults = {
        "data_choice": "Iceland",
        "period": 5,
        "ef_period": 2,
        "frequency": 30,
        "safe_distance": 0,
        "risk_tolerance": 4,
        "limit_positions": False,
        "long_position_limit": None,
        "short_position_limit": None,
        "portfolio_value": 100000,
        "trading_fee": 0.0075
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def color_weights(val):
    if val > 0:
        return "color: green"   # long
    elif val < 0:
        return "color: red"     # short
    else:
        return "color: black"   # zero weight

def color_position(val):
    if val == "Long":
        return "color: green; font-weight: bold"
    elif val == "Short":
        return "color: red; font-weight: bold"
    else:
        return "color: gray"


col1, col2 = st.columns(2)

# Sidebar controls
with st.sidebar:
    st.header("Controls")

    portfolio_value = st.number_input(
        "Total Capital:",
        min_value=1, step=1, 
        value=100000
    )

    trading_fee = st.number_input(
        "Trading Fee (as a percentage, e.g., 0.75 for 0.75%):",
        min_value=0.0, max_value=100.0, step=0.01,
        value=0.75
    ) / 100

    data_choice = st.selectbox(
        "Select Dataset",
        ["Iceland", "Select Custom Portfolio"]
    )

    period = st.number_input(
        "Select the period for data retrieval in years:", 
        min_value=2, max_value=20, step=1,
        value=5
    )
    ef_period = st.number_input(
        "Select the period for efficient frontier calculation in years:",
        min_value=1, max_value=period, step=1,
        value=2
    )

    if st.button("Fetch Data"):
        st.session_state.data_choice = data_choice
        st.session_state.period = period
        st.session_state.ef_period = ef_period
        st.session_state.portfolio_value = portfolio_value
        st.session_state.trading_fee = trading_fee

with st.sidebar:
    st.header("Optimization")

    frequency = st.number_input(
        "Select the frequency:",
        help = tx.FREQUENCY_INFO,
        min_value=1, max_value=3000, step=1,
        value=30
    )

    safe_distance = st.text_input(
        "Select the safe distance",
        help = tx.SAFE_DISTANCE_INFO,
        value= "0.0"   
    )
    if safe_distance.lower() != "inf":
        try:
            safe_distance = float(safe_distance)
        except ValueError:
            st.error("Invalid input for safe distance. Please enter a number or 'inf'.")

    risk_tolerance = st.text_input(
        "Select your risk tolerance (place on efficient frontier):",
        help = tx.RISK_TOLERANCE_INFO,
        value="4"
    )
    if risk_tolerance.lower() != "slope":
        try:
            risk_tolerance = int(risk_tolerance)
        except ValueError:
            st.error("Invalid input for risk tolerance. Please enter an integer or 'slope'.")

    limit_positions = st.checkbox("Limit position sizes", value=False)
    if limit_positions:
        long_position_limit = st.number_input(
            "Select the maximum long-position size as a percentage of the portfolio (e.g., 0.2 for 20%)",
            min_value=0.0, max_value=10.0, step=0.01
        )
        short_position_limit = st.number_input(
            "Select the maximum short-position size as a percentage of the portfolio (e.g., 0.2 for 20%)",
            min_value=0.0, max_value=10.0, step=0.01
        )
    else:
        long_position_limit = None
        short_position_limit = None



    if st.button("Run Optimization"):
        st.session_state.frequency = frequency
        st.session_state.safe_distance = float(safe_distance) if isinstance(safe_distance, (int, float)) else safe_distance
        st.session_state.risk_tolerance = int(risk_tolerance) if isinstance(risk_tolerance, (int, float)) else risk_tolerance
        st.session_state.limit_positions = limit_positions
        st.session_state.long_position_limit = long_position_limit
        st.session_state.short_position_limit = short_position_limit


data = bk.load_data(st.session_state.data_choice, st.session_state.period)
returns, returns_ef = \
    bk.get_returns(
        data, keep_pct=0.9, slice_output=True, 
        ef_period=st.session_state.ef_period
    )
yearly_returns = bk.cal_yearly_returns(returns)
yearly_returns_ef = bk.cal_yearly_returns(returns_ef)
target_returns, stds, weights, risk_index, portfolio_weights = \
    bk.calculate_efficient_frontier(
        returns_ef, yearly_returns_ef, bounded=st.session_state.limit_positions, 
        short_bound=st.session_state.short_position_limit, 
        long_bound=st.session_state.long_position_limit
    )
starting_date = returns.index.min() + pd.DateOffset(years=ef_period)
starting_date = returns.index[returns.index > starting_date][0] 
list_of_expected_returns, list_of_stds, list_of_portfolio_values, list_of_fee_costs, \
trading_dates, rebalance_flags, list_of_weights\
    = bk.rebalance_through_time(
    returns = returns, current_date=starting_date, offset=st.session_state.ef_period, frequency=st.session_state.frequency, 
    risk=st.session_state.risk_tolerance, rebalance_distance=st.session_state.safe_distance, 
    bounded=st.session_state.limit_positions, short_bound=st.session_state.long_position_limit, 
    long_bound=st.session_state.short_position_limit, portfolio_weight=portfolio_weights, 
    fee_rate=st.session_state.trading_fee
)
return_list = []
parameter_list = []
total_return = list_of_portfolio_values[-1] - 1
annual_return_of_portfolio = math.exp((math.log(total_return+1))/(period-ef_period))-1
return_list.append(annual_return_of_portfolio)
parameter_list.append([frequency, st.session_state.safe_distance])

performance_metrics_df = pd.DataFrame({
    "Metric": [
        "Total Return",
        "Total Trading Fees",
        "Annualized Return after cost"
    ],
    
    "Percentage": [
        total_return * 100,
        sum(list_of_fee_costs) * 100,
        annual_return_of_portfolio * 100
    ],

    "Value": [
        total_return*st.session_state.portfolio_value,
        sum(list_of_fee_costs)*st.session_state.portfolio_value,
        None
    ]
})

portfolio_plot_df = pd.DataFrame({
    "Date": trading_dates,
    "Portfolio Value": [value * st.session_state.portfolio_value for value in list_of_portfolio_values],
    "Rebalanced": rebalance_flags
})

weights_history_df = pd.DataFrame(
    list_of_weights,
    index=trading_dates,
    columns=returns.columns
)

with col1:
    st.subheader("Efficient Frontier")
    fig, ax = plt.subplots()
    ax.plot(stds, target_returns[:len(stds)], 
            label="Efficient Frontier"
            )
    ax.scatter(stds[0], target_returns[0], 
                color='red', 
                label="Minimum Variance Portfolio"
                )
    ax.scatter(stds[risk_index], target_returns[risk_index], 
                color='blue', 
                label="Selected point on Efficient Frontier"
                )
    
    ax.set_xlabel("Expected Return")
    ax.set_ylabel("Volatility")
    ax.set_title("Efficient Frontier with Minimum Variance Portfolio (Íslenski markaðurinn)")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)



# Show results
with col2:
    st.subheader("Portfolio Weights")
    weights_df = pd.DataFrame({
        "Weight": portfolio_weights
    })

    weights_df["Position"] = weights_df["Weight"].apply(
        lambda x: "Long" if x > 0 else ("Short" if x < 0 else "Neutral")
    )
    styled_df = weights_df.style \
        .format({"Weight": "{:.2%}"}) \
        .map(color_position, subset=["Position"])
    st.dataframe(styled_df)

    st.subheader("Performance Metrics")
    st.table(performance_metrics_df.style.format({
        "Percentage": "{:.2f}%",
        "Value": lambda x: f"{x:,.0f} kr".replace(",", ".") if pd.notnull(x) else ""
    }))


# ----------------------------
# Visualization
# ----------------------------
st.subheader("Visualization")


fig, ax = plt.subplots(figsize=(12, 5))

# Portfolio line
ax.plot(
    portfolio_plot_df["Date"],
    portfolio_plot_df["Portfolio Value"],
    label="Portfolio Value"
)

# Rebalance points
rebalance_df = portfolio_plot_df[portfolio_plot_df["Rebalanced"]]

ax.scatter(
    rebalance_df["Date"],
    rebalance_df["Portfolio Value"],
    color="red",
    s=50,
    label="Rebalance"
)

ax.set_xlabel("Date")
ax.set_ylabel("Portfolio Value")
ax.set_title("Portfolio Value Through Time")
ax.legend()
ax.grid(True)


st.pyplot(fig)

st.subheader("Position after each Rebalance")
st.dataframe(weights_history_df.style.map(color_weights))