# This is the main entry point of the application

import get_data as gt
import efficient_frontier as ef
import numpy as np
import pandas as pd

### Testing functions ###
#data = gt.get_data(country='iceland', period='5y', interval='1d')
#returns = gt.portfolio_returns(data)
#yearly_returns = gt.cal_yearly_returns(returns)

#print(data)

from get_data import get_data

prices = get_data(ticker="ALVO.IC", period="5y", interval="1d")

print(prices.head())
print(prices.tail())
print(prices.shape)

'''
for i in range(len(list(returns.keys()))):
    print(list(returns.keys())[i],len(returns[list(returns.keys())[i]]))
'''


### main application logic would go here ###


#def main():
#    ...
#    pass