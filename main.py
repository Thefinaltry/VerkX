# This is the main entry point of the application

import get_data as gt
import efficient_frontier as ef
import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### main application logic would go here ###

def main():
    ### Testing functions ###
    data = gt.get_data(country='iceland', period='8y', interval='1d')
    returns = gt.portfolio_returns(data)
    yearly_returns = gt.cal_yearly_returns(returns)

    #returns.to_csv('returns.csv')

    target_returns, stds, weights = ef.calculate_efficient_frontier(returns,yearly_returns)

    plt.figure(figsize=(8,5))
    plt.plot(stds, target_returns[0:len(stds)])
    plt.xlabel("Volatility")
    plt.ylabel("Expected Return")
    plt.title("Efficient Frontier (Íslenski markaðurinn)")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()


