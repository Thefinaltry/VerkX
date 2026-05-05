from operator import gt
import time

import streamlit as st
import matplotlib.pyplot as plt
import functions as f
import pandas as pd
import math

# initializing page
st.markdown("# Results")
st.sidebar.markdown("# Results")

# Page description
st.write("""
        SETJA EH FLOTT HÉR
        """)


### Buttons to trigger the functions in backend.py and display the results ###

if st.session_state.get("data_selected", False) == False:
    st.warning("Please navigate to the Data Selection page, make your selections, and click 'Save Selections' to proceed.")
    st.text("Once you have made your selections and saved them, you can return to this page to see the efficient frontier and other analyses based on your selections.")
    #st.image("https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif", caption="Please make your selections and click 'Save Selections' to proceed.")

elif st.session_state.get("optimization_selected", False) == False:
    st.warning("Please navigate to the Optimization page, make your selections, and click 'Save Selections' to proceed.")
    st.text("Once you have made your selections and saved them, you can return to this page to see the efficient frontier and other analyses based on your selections.")
    #st.image("https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif", caption="Please make your selections and click 'Save Selections' to proceed.")

else:

    # Plot efficient frontier
    if st.button("Plot efficient frontier"):
        # Call the function to plot the efficient frontier
        fig, ax = plt.subplots()
        ax.plot(st.session_state["stds"], st.session_state["target_returns"][:len(st.session_state["stds"])])
        ax.set_xlabel("Volatility")
        ax.set_ylabel("Expected Return")
        ax.set_title("Efficient Frontier (Íslenski markaðurinn)")
        ax.grid(True)

        st.pyplot(fig)

    # Calculate minimum variance portfolio and display it on the efficient frontier plot.
    if st.button("Calculate minimum variance portfolio"):
        # Call the function to calculate the minimum variance portfolio
        fig, ax = plt.subplots()
        ax.plot(st.session_state["stds"], st.session_state["target_returns"][:len(st.session_state["stds"])], 
                label="Efficient Frontier"
                )
        ax.scatter(st.session_state["std_of_min_var"], st.session_state["expected_return_of_min_var"], 
                   color='red', 
                   label="Minimum Variance Portfolio"
                   )
        ax.set_xlabel("Volatility")
        ax.set_ylabel("Expected Return")
        ax.set_title("Efficient Frontier with Minimum Variance Portfolio (Íslenski markaðurinn)")
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

    # Test minimum variance portfolio performance
    if st.button("Test minimum variance portfolio performance"):
        # Call the function to test the minimum variance portfolio
        annual_return_of_min_var, first, start_date, end_date = f.return_of_min_var(st.session_state["returns"], st.session_state["period"], st.session_state["ef_period"], st.session_state["min_var_weights"])
        if st.session_state["ef_period"]:
            st.write(f"A {st.session_state['ef_period']} year period was used to calculate the min-var portfolio ({first.strftime('%Y-%m-%d')} to {start_date.strftime('%Y-%m-%d')}). The weights are:")
        st.write(st.session_state['min_var_weights'])
        st.write(f"Then performance of that portfolio was measured for a {st.session_state['period']-st.session_state['ef_period']} year period ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
        st.write(f"It's average annual performance was: {annual_return_of_min_var*100:.2f}% per year")


    # Test rebalancing strategy performance
    if st.button("Test rebalancing strategy performance"):
    

        figs, list_of_expected_returns, list_of_stds, list_of_portfolio_values, list_of_fee_costs, total_return, annual_return_of_portfolio = f.rebalance_through_time()

        st.write(f"Total return: {total_return*100:.2f}%")
        st.write(f"Annualized return: {annual_return_of_portfolio*100:.2f}%")
        st.write(f"Total trading fees paid: {sum(list_of_fee_costs)*100:.2f}%")

        placeholder = st.empty()

        for fig in figs:
            with placeholder:
                st.pyplot(fig)  # or st.plotly_chart(fig)
            time.sleep(0.8)

    # Compare with 1/n strategy
    if st.button("Compare with 1/n strategy"):
        

        pass

