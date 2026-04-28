import streamlit as st
import backend as bk
import matplotlib.pyplot as plt

st.markdown("# Results")
st.sidebar.markdown("# Results")

st.write("""
        This is the Results page. Here you can view the results of your analysis and optimization.
        You can see the performance of your portfolio, the efficient frontier, and other relevant metrics.
        """)

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


if st.button("Calculate minimum variance portfolio"):
    # Call the function to calculate the minimum variance portfolio
    pass

if st.button("Test minimum variance portfolio performance"):
    # Call the function to test the minimum variance portfolio
    pass

if st.button("Test rebalancing strategy performance"):
    # Call the function to test the rebalancing strategy
    pass

if st.button("Compare with 1/n strategy"):
    # Call the function to compare with 1/n strategy
    pass
