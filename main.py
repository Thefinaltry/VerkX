# This is the main entry point of the application

import get_data as gt
import efficient_frontier as ef
import numpy as np


### Testing functions ###
data = gt.get_data(country='iceland', period='2y', interval='1d')
returns = gt.portfolio_returns(data)

for i in range(len(list(returns.keys()))):
    print(len(returns[list(returns.keys())[i]]))



### main application logic would go here ###


def main():
    ...
    pass


