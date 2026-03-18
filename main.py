# This is the main entry point of the application

import get_data as gt
import efficient_frontier as ef
import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import warnings

<<<<<<< Updated upstream
pd.options.display.float_format = '{:.6f}'.format
=======
### Testing functions ###
data = gt.get_data(country='iceland', period='5y', interval='1d')
returns = gt.portfolio_returns(data)
yearly_returns = gt.cal_yearly_returns(returns)

#print(data)

'''
from get_data import get_data

prices = get_data(ticker="ALVO.IC", period="5y", interval="1d")

print(prices.head())
print(prices.tail())
print(prices.shape)


for i in range(len(list(returns.keys()))):
    print(list(returns.keys())[i],len(returns[list(returns.keys())[i]]))
'''
>>>>>>> Stashed changes

warnings.filterwarnings(
    "ignore",
    message="Values in x were outside bounds during a minimize step",
    category=RuntimeWarning
)

### main application logic would go here ###

def fetch_from_user(slice_output: bool = False):
    period = 0
    efficient_frontier_period = 0
    short_bound = None
    long_bound = None
    while True:
        try:
            period = int(input('Total time period (years): '))
            if period <= 1:
                print("Period must be greater than 1.")
                print()
                continue
            break
        except ValueError:
            print("Invalid input... Please enter an integer.")
            print()
    
    if slice_output:
        while True:
            try:
                efficient_frontier_period = int(input('Number of years to calculate efficient frontier (years): '))
                
                if 1 <= efficient_frontier_period <= period - 1:
                    break
                else:
                    print(f"Invalid time period... Must be a number between 1-{period-1}")
            except ValueError:
                print("Invalid input... Please enter an integer.")
    else:
        efficient_frontier_period = 0

    while True:
        try:
            bounds = input('Limit position size? (y/n): ')
            if bounds.lower() not in ['y', 'n']:
                print("Invalid input... Please enter y or n (yes or no)")
                print()
                continue
            if bounds.lower() == 'y':
                while True:
                    try:
                        short_bound = input("How large can SHORT positions get (%)?: ")
                        if short_bound.lower() in ["inf", 'infinite', 'max', 'unbound']:
                            short_bound == None
                        else:    
                            short_bound = int(short_bound)
                            if short_bound <= 0:
                                short_bound = -1*short_bound
                        while True:
                            try:
                                long_bound = input("How large can LONG positions get (%)?: ")
                                if long_bound.lower() in ["inf", 'infinite', 'max', 'unbound']:
                                    long_bound == None
                                else:    
                                    long_bound = int(long_bound)
                                    if long_bound <= 0:
                                        print("Invalid input... long positions can not be negative (or zero)")
                                        print()
                                        continue
                                break
                            except ValueError:
                                print("Invalid input... Please enter an integer")
                                print()
                        break
                    except ValueError:
                        print("Invalid input... Please enter an integer")
                        print()
            break
        except ValueError:
            print("Invalid input... Please enter y or n (yes or no)")
            print()
    
    if short_bound != None:
        short_bound = float(short_bound)/100
    if short_bound != None:
        long_bound = float(long_bound)/100

    return period, efficient_frontier_period, short_bound, long_bound

def menu():
    while True:
        print("\n------ Efficient frontier (Iceland) ------")
        print("1. Plot efficient frontier")
        print("2. Calculate minimum variance portfolio")
        print("3. Test minimum variance porftolio performance")
        print("4. exit")

        choice = input("Choose an option (1-4): ")

        if choice in ["1", "2", "3", "4"]:
            return int(choice)
        else:
            print("Invalid choice. Please select a number between 1 and 4.")
    

def main():
    while True:
        choice = menu()

        if choice == 1:
            period, _, short_bound, long_bound = fetch_from_user()
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
            period, _, short_bound, long_bound = fetch_from_user()
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
            period, ef_period, short_bound, long_bound = fetch_from_user(True)
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
            break
        

if __name__ == "__main__":
    main()
