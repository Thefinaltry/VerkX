import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
from core import efficient_frontier as ef
from core import get_data as gt
from core import rebalance as rb


# =========================
# Cache data (IMPORTANT)
# =========================
@st.cache_data
def load_data(period_string):
    return gt.get_data(country="iceland", period=period_string, interval="1d")


# =========================
# UI
# =========================
st.title("Efficient Frontier (Ísland)")

with st.sidebar:
    st.header("Settings")

    choice = st.selectbox(
        "Choose an option",
        [
            "Plot efficient frontier",
            "Minimum variance portfolio",
            "Test min-var performance",
            "Test rebalancing strategy"
        ]
    )

    period = st.number_input(
        "Total time period (years):",
        min_value=1,
        step=1,
        value=5
    )

    # Logic-based toggles
    if choice in ["Test min-var performance", "Test rebalancing strategy"]:
        slice_output = True
    else:
        slice_output = st.checkbox("Enable efficient frontier slicing")

    rebalance = (choice == "Test rebalancing strategy")


# =========================
# Main Inputs
# =========================
st.header("Portfolio Settings")

if slice_output:
    efficient_frontier_period = st.number_input(
        f"Years to calculate efficient frontier (1 to {period-1}):",
        min_value=1,
        max_value=period-1,
        step=1,
        value=1
    )
else:
    efficient_frontier_period = 0

ef_period = efficient_frontier_period

# --- Bounds ---
st.subheader("Position Size Limits")
limit_positions = st.radio("Limit position size?", ["No", "Yes"])

short_bound, long_bound = None, None

if limit_positions == "Yes":
    short_input = st.text_input("Max SHORT (%) or 'inf':", value="50")
    long_input = st.text_input("Max LONG (%) or 'inf':", value="100")

    if short_input.lower() not in ["inf", "infinite", "max", "unbound"]:
        try:
            short_bound = abs(int(short_input)) / 100
        except:
            st.error("Invalid short bound")

    if long_input.lower() not in ["inf", "infinite", "max", "unbound"]:
        try:
            val = int(long_input)
            if val > 0:
                long_bound = val / 100
            else:
                st.error("Long must be positive")
        except:
            st.error("Invalid long bound")

# --- Rebalancing ---
if rebalance:
    st.subheader("Rebalancing Settings")

    risk_input = st.text_input("Risk (1–10 or 'slope'):", value="5")

    if risk_input.lower() == "slope":
        risk = "slope"
    else:
        try:
            risk = int(risk_input)
            if not (1 <= risk <= 10):
                st.error("Risk must be 1–10")
                risk = None
        except:
            st.error("Invalid risk")
            risk = None

    dist_input = st.text_input("Distance from frontier (%) or 'inf':", value="5")

    if dist_input == "inf":
        rebalance_distance = float("inf")
    else:
        try:
            rebalance_distance = int(dist_input)
            if rebalance_distance < 0:
                st.error("Must be ≥ 0")
                rebalance_distance = None
            else:
                rebalance_distance = rebalance_distance / 100  # convert % to decimal
        except:
            st.error("Invalid distance")
            rebalance_distance = None

    max_days = max(1, int((period - ef_period) * 252 * 0.5))

    frequency = st.number_input(
        f"Frequency (days, max {max_days}):",
        min_value=1,
        max_value=max_days,
        value=min(30, max_days)
    )

# =========================
# Run Button
# =========================
run = st.button("Run")

if not run:
    st.stop()

# Guard against invalid inputs
if rebalance and (risk is None or rebalance_distance is None):
    st.stop()

# =========================
# Load Data
# =========================
period_string = f"{period}y"
data = load_data(period_string)

# =========================
# 1. Efficient Frontier
# =========================
if choice == "Plot efficient frontier":
    returns, _ = gt.get_returns(data)
    yearly_returns = gt.cal_yearly_returns(returns)

    if short_bound is not None or long_bound is not None:
        target_returns, stds, _ = ef.calculate_efficient_frontier(
            returns, yearly_returns, True, short_bound, long_bound
        )
    else:
        target_returns, stds, _ = ef.calculate_efficient_frontier(
            returns, yearly_returns, False
        )

    fig, ax = plt.subplots()
    ax.plot(stds, target_returns[:len(stds)])
    ax.set_xlabel("Volatility")
    ax.set_ylabel("Expected Return")
    ax.grid(True)

    st.pyplot(fig)

# =========================
# 2. Min Variance
# =========================
elif choice == "Minimum variance portfolio":
    returns, _ = gt.get_returns(data)
    yearly_returns = gt.cal_yearly_returns(returns)

    if short_bound is not None or long_bound is not None:
        w, ret, std = ef.calculate_min_var(
            returns, yearly_returns, True, short_bound, long_bound
        )
    else:
        w, ret, std = ef.calculate_min_var(
            returns, yearly_returns, False
        )

    st.write("Weights:", w)
    st.write("Return:", ret)
    st.write("Volatility:", std)

# =========================
# 3. Test Min Var
# =========================
elif choice == "Test min-var performance":
    returns, ef_returns = gt.get_returns(
        data, keep_pct=0.9, slice_output=True, ef_period=ef_period
    )

    yearly_returns_ef = gt.cal_yearly_returns(ef_returns)

    if short_bound is not None or long_bound is not None:
        w, _, _ = ef.calculate_min_var(
            ef_returns, yearly_returns_ef, True, short_bound, long_bound
        )
    else:
        w, _, _ = ef.calculate_min_var(
            ef_returns, yearly_returns_ef, False
        )

    annual_return, first, start, end = ef.return_of_min_var(
        returns, period, ef_period, w
    )

    st.write(f"Training: {first.date()} → {start.date()}")
    st.write(f"Testing: {start.date()} → {end.date()}")
    st.write("Weights:", w)
    st.success(f"Annual return: {annual_return*100:.2f}%")

# =========================
# 4. Rebalancing
# =========================
elif choice == "Test rebalancing strategy":
    returns, ef_returns = gt.get_returns(
        data, keep_pct=0.9, slice_output=True, ef_period=ef_period
    )

    start_date = returns.index.min() + pd.DateOffset(years=ef_period)
    start_date = returns.index[returns.index > start_date][0]

    if short_bound is not None or long_bound is not None:
        result = rb.rebalance_engine(
            returns, ef_returns, start_date,
            ef_period, frequency, risk, rebalance_distance,
            True, short_bound, long_bound
        )
    else:
        result = rb.rebalance_engine(
            returns, ef_returns, start_date,
            ef_period, frequency, risk, rebalance_distance,
            False
        )

    exp_ret = result["exp_returns"]
    stds = result["stds"]
    values = result["values"]
    fees = result["fees"]

    total_return = values[-1] - 1
    annual_return = math.exp(
        math.log(total_return + 1) / (period - ef_period)
    ) - 1

    st.write(f"Total return: {total_return*100:.2f}%")
    st.write(f"Annualized: {annual_return*100:.2f}%")
    st.write(f"Fees: {sum(fees)*100:.2f}%")

    fig, ax = plt.subplots()
    ax.plot(stds, exp_ret)
    ax.set_title("Rebalancing Path")

    st.pyplot(fig)
