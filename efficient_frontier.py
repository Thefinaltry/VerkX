import numpy as np
import pandas as pd
from scipy.optimize import minimize
import math


### Testing functions ###

def get_covariance_matrix(returns):
    cov_matrix = returns.cov()
    cov_annual = cov_matrix * 252
    cov_inv = pd.DataFrame(
        np.linalg.inv(cov_annual.values),
        index=cov_annual.index,
        columns=cov_annual.columns
    )
    return cov_annual, cov_inv

def calculate_min_var(returns:pd.DataFrame, yearly_returns:pd.DataFrame, bounded: bool = True, short_bound: float = 0.15, long_bound: float = 0.15):
    cov_annual, cov_inv = get_covariance_matrix(returns)
    if bounded:
        mu = yearly_returns.loc[cov_annual.index]
        n = len(mu)
        x0 = np.ones(n) / n

        if short_bound == None:
            bounds = [(short_bound, long_bound)] * n
        else:
            bounds = [(-short_bound, long_bound)] * n
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
        ]

        result = minimize(
            fun=lambda w: w @ cov_annual.values @ w,
            x0=x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )
        min_var_weights = pd.Series(result.x, index=mu.index)
        expected_return_of_min_var = yearly_returns.T @ min_var_weights
        std_of_min_var = np.sqrt(result.x @ cov_annual.values @ result.x)
        return [min_var_weights, expected_return_of_min_var, std_of_min_var]
    else:
        ones = pd.Series(1.0, index=cov_inv.index)
        numerator = cov_inv @ ones
        denominator = ones.T @ cov_inv @ ones
        min_var_weights = numerator / denominator

        
        expected_return_of_min_var = yearly_returns.T @ min_var_weights
        std_of_min_var = 1/np.sqrt(denominator)
        return [min_var_weights, expected_return_of_min_var, std_of_min_var]

def bounded_portfolio_weights(cov_annual: pd.DataFrame, mu: pd.Series, target_return: float, short_bound: float = 0.15, long_bound: float = 0.15, x0=None) -> pd.Series:
    n = len(mu)
    if x0 is None:
        x0 = np.ones(n) / n
    bounds = [(-short_bound, long_bound)] * n
    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
        {"type": "eq", "fun": lambda w: mu.values @ w - target_return},
    ]

    result = minimize(fun=lambda w: w @ cov_annual.values @ w, x0=x0, method="SLSQP", bounds=bounds, constraints=constraints, options={"maxiter": 2000, "ftol": 1e-9})

    if not result.success:
        return None
        #raise ValueError(f"Optimization failed for target return {target_return:.4f}: {result.message}")

    return pd.Series(result.x, index=mu.index)

def calculate_efficient_frontier(returns:pd.DataFrame,yearly_returns:pd.DataFrame, bounded: bool = True, short_bound: float = 0.15, long_bound: float = 0.15):
    cov_annual, cov_inv = get_covariance_matrix(returns)
    min_var_weights, expected_return_of_min_var, _ = calculate_min_var(returns, yearly_returns, bounded, short_bound, long_bound)

    #print(min_var_weights)
    ones = pd.Series(1.0, index=cov_inv.index)
    mu = yearly_returns.loc[cov_inv.index]
    denominator = ones.T @ cov_inv @ ones

    target_returns = np.arange(float(expected_return_of_min_var), 0.50 + 1e-12, 0.0025)
    stds = []
    weights = []

    x0 = np.ones(len(mu)) / len(mu)

    for i in target_returns:
        if bounded:
            w = bounded_portfolio_weights(cov_annual, mu, i, short_bound, long_bound, x0)
        else:
            w = ((i * ((cov_inv @ mu * (denominator))-((cov_inv @ ones) * (ones.T @ cov_inv @ mu)))) + ((cov_inv @ ones) * (mu.T @ cov_inv @ mu)) - ((cov_inv @ mu) * (mu.T @ cov_inv @ ones)))/((denominator * (mu.T @ cov_inv @ mu))-((ones.T @ cov_inv @ mu) * (mu.T @ cov_inv @ ones)))
        if w is None:
            #print(f"Maximum feasible return is below {i:.4f}")
            break
        
        weights.append(w)
        std = np.sqrt(w @ cov_annual @ w.T)
        stds.append(std)
        x0 = w.values
    return target_returns, stds, weights

def return_of_min_var(returns: pd.DataFrame, period: int, ef_period: int, min_var_weights: pd.Series):
    first = returns.index.min()
    start_date = first + pd.DateOffset(years=ef_period)
    start_date = returns.index[returns.index >= start_date][0]

    end_date = returns.index.max()

    period_returns = returns.loc[start_date:end_date]
    #period_returns.to_csv('period_returns.csv')
    total_returns = (1 + period_returns).prod() - 1

    min_var_return = total_returns @ min_var_weights
    annual_return_of_min_var = math.exp((math.log(min_var_return+1))/(period-ef_period))-1

    return annual_return_of_min_var, first, start_date, end_date
