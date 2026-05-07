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

if st.session_state.get("data_selected", False) or st.session_state.get("optimization_selected", False) == False:
    st.warning("Please navigate to the Data Selection page, make your selections, and click 'Save Selections' to proceed.")
    st.text("Once you have made your selections and saved them, you can return to this page to see the efficient frontier and other analyses based on your selections.")
    #st.image("https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif", caption="Please make your selections and click 'Save Selections' to proceed.")

else: 

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

            return_list = []
            parameter_list = []
            strategy_return_list = []
            no_rebalance_difference_list = []
            period = st.session_state.get("period")
            period_string = str(period)+'y'
            ef_period = st.session_state.get("ef_period")
            short_bound = st.session_state.get("short_position_limit")
            long_bound = st.session_state.get("long_position_limit")
            frequency_list = [i for i in range(1,1080+1,1)]
            risk = st.session_state.get("risk-level")
            rebalance_distance_list = ['inf',0] #0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.10
            display_graph = False

            counter = 0
            nr_of_runs = ((len(rebalance_distance_list)-1)*len(frequency_list))+1
            _,annualized_return_of_one_over_n = f.simulate_one_over_n(simulation_period=(period-ef_period),period=period,ask_for_input=False)

            data = gt.get_data(country='iceland', period=period_string, interval='1d')
            returns,ef_returns = f.get_returns(data,keep_pct=0.9,slice_output=True,ef_period=ef_period)
            yearly_returns_ef = f.cal_yearly_returns(ef_returns)

            for j in frequency_list:
                frequency = j
                for i in rebalance_distance_list:
                    rebalance_distance = i
                    if rebalance_distance == 'inf':
                        if counter != 0:
                            continue
                    else:
                        rebalance_distance = i*100

                    #if risk == 1:
                    starting_date = returns.index.min() + pd.DateOffset(years=ef_period)
                    starting_date = returns.index[returns.index > starting_date][0]           
                    end_date = returns.index.max()
                    #print(starting_date, end_date)
                
                    if short_bound != None or long_bound != None:
                        list_of_expected_returns, list_of_stds, list_of_portfolio_values, list_of_fee_costs = rb.rebalance_through_time(display_graph, returns, ef_returns, starting_date, ef_period, frequency, risk, rebalance_distance, True, short_bound, long_bound)
                    else:
                        list_of_expected_returns, list_of_stds, list_of_portfolio_values, list_of_fee_costs = rb.rebalance_through_time(display_graph, returns, ef_returns, starting_date, ef_period, frequency, risk, rebalance_distance, False)

                    #print(list_of_portfolio_values)
                    print()
                    total_return = list_of_portfolio_values[-1] - 1
                    annual_return_of_portfolio = math.exp((math.log(total_return+1))/(period-ef_period))-1
                    return_list.append(annual_return_of_portfolio)
                    if rebalance_distance == 'inf':
                        parameter_list.append([frequency, 'inf'])
                    else:
                        parameter_list.append([frequency, rebalance_distance / 100])

                    counter +=1
                    print(f"{counter}/{nr_of_runs}")
                    print(f"Total return: {total_return*100:.2f}%")
                    print(f"Annualized return: {annual_return_of_portfolio*100:.2f}%")
                    print(f"Total trading fees paid: {sum(list_of_fee_costs)*100:.2f}%")
                    
                    if rebalance_distance != 'inf':
                        strategy_return_list.append(annual_return_of_portfolio)
                        no_rebalance_difference_list.append(annual_return_of_portfolio-return_list[0])

            labels = []

            for frequency, rebalance_distance in parameter_list:
                if rebalance_distance == 'inf':
                    continue

                labels.append(f"{frequency}d, {rebalance_distance*100:.0f}%")

            x = np.arange(len(strategy_return_list))

            plt.figure(figsize=(14, 6))
            plt.bar(x, [value * 100 for value in strategy_return_list])

            plt.axhline(
                annualized_return_of_one_over_n * 100,
                linestyle=":",
                linewidth=2,
                label="1/N return"
            )

            tick_step = max(1, len(labels) // 30)

            plt.xticks(
                x[::tick_step],
                labels[::tick_step],
                rotation=90
            )

            plt.xlabel("Rebalancing frequency and safe distance")
            plt.ylabel("Annualized return (%)")
            plt.title("Rebalancing strategy returns with 1/N reference line")
            plt.legend()
            plt.tight_layout()
            plt.show()

            plt.figure(figsize=(14, 6))
            plt.bar(x, [value * 100 for value in no_rebalance_difference_list])
            plt.axhline(0, linewidth=1)
            tick_step = max(1, len(labels) // 30)

            plt.xticks(
                x[::tick_step],
                labels[::tick_step],
                rotation=90
            )

            plt.xlabel("Rebalancing frequency and safe distance")
            plt.ylabel("Difference in annualized return (% points)")
            plt.title("Rebalancing strategy minus no-rebalance strategy")
            plt.tight_layout()
            plt.show()

            max_value = max(return_list)
            max_index = return_list.index(max_value)

            best_parameters = parameter_list[max_index]

            print()
            print(f"Max return: {max_value*100:.2f}%")
            print(f"Rebalancing frequency: {best_parameters[0]} days, Safe distance: {best_parameters[1]*100:.0f}%")

