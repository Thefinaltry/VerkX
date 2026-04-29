import streamlit as st
import backend as bk
import matplotlib.pyplot as plt

# initializing page
st.markdown("# Results")
st.sidebar.markdown("# Results")

# Page description
st.write("""
        SETJA EH FLOTT HÉR
        """)


### Buttons to trigger the functions in backend.py and display the results ###

# Plot efficient frontier
if st.button("Plot efficient frontier"):
    # Call the function to plot the efficient frontier
    target_returns, stds, weights = bk.plot_efficient_frontier()
    fig, ax = plt.subplots()
    ax.plot(stds, target_returns[:len(stds)])
    ax.set_xlabel("Volatility")
    ax.set_ylabel("Expected Return")
    ax.set_title("Efficient Frontier (Íslenski markaðurinn)")
    ax.grid(True)

    st.pyplot(fig)

# Calculate minimum variance portfolio and display it on the efficient frontier plot.
if st.button("Calculate minimum variance portfolio"):
    # Call the function to calculate the minimum variance portfolio
    pass

# Test minimum variance portfolio performance
if st.button("Test minimum variance portfolio performance"):
    # Call the function to test the minimum variance portfolio
    pass

# Test rebalancing strategy performance
if st.button("Test rebalancing strategy performance"):
    # Call the function to test the rebalancing strategy
    pass

# Compare with 1/n strategy
if st.button("Compare with 1/n strategy"):
    # Call the function to compare with 1/n strategy
    pass
