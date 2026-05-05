import streamlit as st

st.markdown("# Optimization")
st.sidebar.markdown("# Optimization")

st.write("""
        SETJA EH FLOTT HÉR!!!!!
        """)


# Rebalancing strategy selection

# Risk-based rebalancing strategy
Risk_based_rebalance = st.checkbox("Risk-based rebalancing strategy", value=False)
if Risk_based_rebalance:
        risk_level = st.number_input("Select a risk level", min_value=1, max_value=10, step=1)

# Slope-based rebalancing strategy
slope_based_rebalance = st.checkbox("Slope-based rebalancing strategy", value=False)
if slope_based_rebalance:
        slope = True

# Drift-based rebalancing strategy
drift_based_rebalance = st.checkbox("Drift-based rebalancing strategy", value=False)
if drift_based_rebalance:
        drift_margine = st.number_input("Select a drift margine (e.g., 0.05 for 5%)", min_value=0.0, max_value=1.0, step=0.01)

# Position size limits selection
select_limits = st.checkbox("Select limits position size", value=False)
if select_limits:
        long_position_limit = st.number_input("Select the maximum long-position size as a percentage of the portfolio (e.g., 0.2 for 20%)", min_value=0.0, max_value=1.0, step=0.01)
        short_position_limit = st.number_input("Select the maximum short-position size as a percentage of the portfolio (e.g., 0.2 for 20%)", min_value=0.0, max_value=1.0, step=0.01)
else:
        long_position_limit = None
        short_position_limit = None

save_button = st.button("Save Selections")
if save_button:
    st.session_state.update({
        "risk-level": risk_level if Risk_based_rebalance else 1,
        "slope": slope_based_rebalance,
        "drift-margine": drift_margine if drift_based_rebalance else None,
        "long_position_limit": long_position_limit,
        "short_position_limit": short_position_limit,
        "optimization_selected": True})
    st.switch_page("results.py")
else:
        st.warning("Please make your selections and click 'Save Selections' to proceed.")
        st.session_state["optimization_selected"] = False

