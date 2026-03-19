# This is the main entry point of the application

import get_data as gt
import efficient_frontier as ef
import rebalance as rb
import UI_demo as ui
import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

pd.options.display.float_format = '{:.6f}'.format

warnings.filterwarnings(
    "ignore",
    message="Values in x were outside bounds during a minimize step",
    category=RuntimeWarning
)

### main application logic would go here ###

def main():
    while True:
        choice = ui.menu()

        if choice == 1:
            period, _, short_bound, long_bound = ui.fetch_from_user()
            period_string = str(period)+'y'
            data = gt.get_data(country='iceland', period=period_string, interval='1d')
            returns,_ = gt.get_returns(data)
            yearly_returns = gt.cal_yearly_returns(returns)
            if short_bound != None or long_bound != None:
                target_returns, stds, weights = ef.calculate_efficient_frontier(returns,yearly_returns,True,short_bound,long_bound)
            else:
                target_returns, stds, weights = ef.calculate_efficient_frontier(returns,yearly_returns,False)
            plt.figure(figsize=(8,5))
            plt.plot(stds, target_returns[0:len(stds)])
            plt.xlabel("Volatility")
            plt.ylabel("Expected Return")
            plt.title("Efficient Frontier (Íslenski markaðurinn)")
            plt.grid(True)
            plt.show()

        if choice == 2:
            period, _, short_bound, long_bound = ui.fetch_from_user()
            period_string = str(period)+'y'
            data = gt.get_data(country='iceland', period=period_string, interval='1d')
            returns,_ = gt.get_returns(data)
            yearly_returns = gt.cal_yearly_returns(returns)
            if short_bound != None or long_bound != None:
                min_var_weights, expected_return_of_min_var, std_of_min_var = ef.calculate_min_var(returns,yearly_returns,True,short_bound,long_bound)
            else:
                min_var_weights, expected_return_of_min_var, std_of_min_var = ef.calculate_min_var(returns,yearly_returns,False)
            print("Min-var porftolio weights:")
            print(min_var_weights)
            print('Expected return:', expected_return_of_min_var)
            print('Volatility:', std_of_min_var)
            print()

        if choice == 3:
        ### Testing functions ###
            period, ef_period, short_bound, long_bound = ui.fetch_from_user(True)
            period_string = str(period)+'y'

            data = gt.get_data(country='iceland', period=period_string, interval='1d')
            _,ef_returns = gt.get_returns(data,keep_pct=0.9,slice_output=True,ef_period=ef_period)
            returns,_ = gt.get_returns(data)
            
            yearly_returns_ef = gt.cal_yearly_returns(ef_returns)
            
            if short_bound != None or long_bound != None:
                target_returns, stds, weights = ef.calculate_efficient_frontier(ef_returns,yearly_returns_ef, True, short_bound, long_bound)
                min_var_weights,expected_return_of_min_var, std_of_min_var = ef.calculate_min_var(ef_returns,yearly_returns_ef, True, short_bound, long_bound)
            else:
                target_returns, stds, weights = ef.calculate_efficient_frontier(ef_returns,yearly_returns_ef, False)
                min_var_weights,expected_return_of_min_var, std_of_min_var = ef.calculate_min_var(ef_returns,yearly_returns_ef, False)  
            
            annual_return_of_min_var, first, start_date, end_date = ef.return_of_min_var(returns,period,ef_period,min_var_weights)
            print()
            print(f"A {ef_period} year period was used to calculate the min-var portfolio ({first.strftime('%Y-%m-%d')} to {start_date.strftime('%Y-%m-%d')}). The weights are:")
            print(min_var_weights)
            print()
            print(f"Then performance of that portfolio was measured for a {period-ef_period} year period ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
            print(f"It's average annual performance was: {annual_return_of_min_var*100:.2f}% per year")
            print()
        
        if choice == 4:
            period, ef_period, short_bound, long_bound = ui.fetch_from_user(True)
            period_string = str(period)+'y'

            data = gt.get_data(country='iceland', period=period_string, interval='1d')
            returns,ef_returns = gt.get_returns(data,keep_pct=0.9,slice_output=True,ef_period=ef_period)
            yearly_returns_ef = gt.cal_yearly_returns(ef_returns)
            print(returns.index.min())
            starting_date = returns.index.min() + pd.DateOffset(years=ef_period)
            starting_date = returns.index[returns.index > starting_date][0]
            end_date = returns.index.max()
            
            if short_bound != None or long_bound != None:
                rb.rebalance_through_time(returns, starting_date, 1, True, short_bound, long_bound)
            else:
                rb.rebalance_through_time(returns, starting_date, 1, False)

        if choice == 5:
            break
        

if __name__ == "__main__":
    main()
