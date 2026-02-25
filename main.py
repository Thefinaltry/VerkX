# This is the main entry point of the application

import get_data as gt
import efficient_frontier as ef
import numpy as np
import pandas as pd

### Testing functions ###
data = gt.get_data(country='iceland', period='5y', interval='1d')
returns = gt.portfolio_returns(data)
yearly_returns = gt.cal_yearly_returns(returns)

print(data)

#print(yearly_returns)

#cov_matrix = ef.get_covariance_matrix(returns)




'''
for i in range(len(list(returns.keys()))):
    print(list(returns.keys())[i],len(returns[list(returns.keys())[i]]))
'''


