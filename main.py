# This is the main entry point of the application

import get_data as gt
import efficient_frontier as ef
import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



### Testing functions ###
data = gt.get_data(country='iceland', period='8y', interval='1d')
returns = gt.portfolio_returns(data)
yearly_returns = gt.cal_yearly_returns(returns)

#returns.to_csv('returns.csv')

cov_matrix = returns.cov()
cov_annual = cov_matrix * 252
cov_inv = pd.DataFrame(
    np.linalg.inv(cov_annual.values),
    index=cov_annual.index,
    columns=cov_annual.columns
)

ones = pd.Series(1.0, index=cov_inv.index)
numerator = cov_inv @ ones
denominator = ones.T @ cov_inv @ ones
min_var_weights = numerator / denominator
#print(min_var_weights)
#print("sum:", min_var_weights.sum())

print(yearly_returns.T)
expected_return_of_min_var = yearly_returns.T @ min_var_weights
std_of_min_var = 1/np.sqrt(denominator)
print("Expected return:",expected_return_of_min_var)
print("Standard deviation:", std_of_min_var)
print(sum(min_var_weights))

#mu = yearly_returns.loc[cov_inv.index].to_numpy().reshape(-1, 1)
mu = yearly_returns.loc[cov_inv.index]

target_returns = np.arange(float(expected_return_of_min_var), 0.50 + 1e-12, 0.0025)
stds = []

for i in target_returns:
    w = ((i * ((cov_inv @ mu * (denominator))-((cov_inv @ ones) * (ones.T @ cov_inv @ mu)))) + ((cov_inv @ ones) * (mu.T @ cov_inv @ mu)) - ((cov_inv @ mu) * (mu.T @ cov_inv @ ones)))/((denominator * (mu.T @ cov_inv @ mu))-((ones.T @ cov_inv @ mu) * (mu.T @ cov_inv @ ones)))
    std = np.sqrt(w @ cov_annual @ w.T)
    stds.append(std)

plt.figure(figsize=(8,5))
plt.plot(stds, target_returns)
plt.xlabel("Volatility")
plt.ylabel("Expected Return")
plt.title("Efficient Frontier (Íslenski markaðurinn)")
plt.grid(True)
plt.show()



'''
for i in range(len(list(returns.keys()))):
    print(list(returns.keys())[i],len(returns[list(returns.keys())[i]]))
'''


### main application logic would go here ###


def main():
    ...
    pass


