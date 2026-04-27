import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import math
import matplotlib.pyplot as plt
import pandas as pd
from core import get_data as gt
import core.rebalance  as rb
from core import efficient_frontier as ef


@st.cache_data
def load_data(period_string):
    return gt.get_data(country="iceland", period=period_string, interval="1d")


st.title("Efficient Frontier (Ísland)")

with st.sidebar:
    choice = st.selectbox(
        "Choose an option",
        [
            "Plot efficient frontier",
            "Minimum variance portfolio",
            "Test min-var performance",
            "Test rebalancing strategy"
        ]
    )

    period = st.number_input("Years", 2, 20, 5)


run = st.button("Run")

if not run:
    st.stop()


data = load_data(f"{period}y")

# ------------------------
# REBALANCING
# ------------------------
if choice == "Test rebalancing strategy":

    returns, ef_returns = gt.get_returns(
        data, keep_pct=0.9, slice_output=True, ef_period=1
    )

    start_date = returns.index.min() + pd.DateOffset(years=1)
    start_date = returns.index[returns.index > start_date][0]

    result = rb.rebalance_engine(
        returns,
        ef_returns,
        start_date,
        offset=1,
        frequency=30,
        risk=1,
        rebalance_distance=0.05,
        bounded=False
    )

    # --- plot ---
    fig, ax = plt.subplots()
    ax.plot(result["stds"], result["exp_returns"])
    ax.set_title("Rebalancing Path")
    st.pyplot(fig)

    # --- metrics ---
    total_return = result["values"][-1] - 1
    st.write("Total return:", f"{total_return*100:.2f}%")
    st.write("Fees:", f"{sum(result['fees'])*100:.2f}%")
