import streamlit as st
import functions as f

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
        drift_margine = st.number_input("Select a drift margine (e.g., 0.05 for 5%)", min_value=0, max_value=None, step=1)

# Position size limits selection
limits = st.checkbox("Select limits position size", value=False)
if limits:
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
        "drift-margine": drift_margine if drift_based_rebalance else 0,
        "limits": limits,
        "long_position_limit": long_position_limit,
        "short_position_limit": short_position_limit,
        "optimization_selected": True})
    
    if st.session_state.get("limits"):
        target_returns, stds, weights = f.calculate_efficient_frontier(st.session_state.get("returns"),st.session_state.get("yearly_returns"),
                                                                     True,st.session_state.get("short_position_limit"),st.session_state.get("long_position_limit"))
    else:
        target_returns, stds, weights = f.calculate_efficient_frontier(st.session_state.get("returns"),st.session_state.get("yearly_returns"),
                                                                     False)
    
    cov, cov_inv = f.get_covariance_matrix(target_returns)

    st.session_state.update({
        "target_returns": target_returns,
        "ef_stds": stds,
        "weights": weights,
        "min_var_weights": weights[0],
        "expected_return_of_min_var": target_returns[0],
        "std_of_min_var": stds[0],
        "cov_annual_matrix": cov,
        "inv_cov_matrix": cov_inv 
    })


    st.switch_page("results.py")
else:
        st.warning("Please make your selections and click 'Save Selections' to proceed.")
        st.session_state["optimization_selected"] = False

