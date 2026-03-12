import numpy as np
import pandas as pd
from scipy.optimize import minimize


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

def calculate_min_var(returns:pd.DataFrame, yearly_returns:pd.DataFrame, bounded: bool = True, bound: float = 0.15):
    cov_annual, cov_inv = get_covariance_matrix(returns)
    if bounded:
        mu = yearly_returns.loc[cov_annual.index]
        n = len(mu)
        x0 = np.ones(n) / n
        bounds = [(-bound, bound)] * n
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

def bounded_portfolio_weights(cov_annual: pd.DataFrame, mu: pd.Series, target_return: float, bound: float = 0.15) -> pd.Series:
    n = len(mu)
    x0 = np.ones(n) / n
    bounds = [(-bound, bound)] * n
    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
        {"type": "eq", "fun": lambda w: mu.values @ w - target_return},
    ]

    result = minimize(fun=lambda w: w @ cov_annual.values @ w, x0=x0, method="SLSQP", bounds=bounds, constraints=constraints)

    if not result.success:
        raise ValueError(f"Optimization failed for target return {target_return:.4f}: {result.message}")

    return pd.Series(result.x, index=mu.index)

def calculate_efficient_frontier(returns:pd.DataFrame,yearly_returns:pd.DataFrame, bounded: bool = True, bound: float = 0.15):
    cov_annual, cov_inv = get_covariance_matrix(returns)
    min_var_weights, expected_return_of_min_var, _ = calculate_min_var(returns, yearly_returns)

    print(min_var_weights)
    ones = pd.Series(1.0, index=cov_inv.index)
    mu = yearly_returns.loc[cov_inv.index]
    denominator = ones.T @ cov_inv @ ones

    target_returns = np.arange(float(expected_return_of_min_var), 0.50 + 1e-12, 0.0025)
    stds = []
    weights = []

    counter = 0
    for i in target_returns:
        if bounded:
            w = ((i * ((cov_inv @ mu * (denominator))-((cov_inv @ ones) * (ones.T @ cov_inv @ mu)))) + ((cov_inv @ ones) * (mu.T @ cov_inv @ mu)) - ((cov_inv @ mu) * (mu.T @ cov_inv @ ones)))/((denominator * (mu.T @ cov_inv @ mu))-((ones.T @ cov_inv @ mu) * (mu.T @ cov_inv @ ones)))
        else:
            w = bounded_portfolio_weights(cov_annual, mu, i, bound)
        weights.append(w)
        std = np.sqrt(w @ cov_annual @ w.T)
        stds.append(std)
        if counter == 0:
            print(w)
        counter += 1
    return target_returns, stds, weights

def portfolio_weights(cov_matrix:pd.DataFrame, exp_returns:pd.Series, target_return:float):
    
    """
    Calculates the portfolio weights for a given target return using the efficient frontier method.
    Args:
        cov_matrix (pandas.DataFrame): Covariance matrix of asset returns.
        exp_returns (pandas.Series): Expected returns of assets.
        target_return (float): Target return for the portfolio.
    Returns:
        pandas.Series: Portfolio weights for each asset.
    """
    
    inv_cov = np.linalg.inv(cov_matrix)
    ones = np.ones(len(exp_returns))

    A = ones.T @ inv_cov @ ones
    B = ones.T @ inv_cov @ exp_returns
    C = exp_returns.T @ inv_cov @ exp_returns

    lambda_val = (C - B * target_return) / (A * C - B ** 2)
    gamma_val = (A * target_return - B) / (A * C - B ** 2)

    weights = inv_cov @ (lambda_val * ones + gamma_val * exp_returns)

    return pd.Series(weights, index=exp_returns.index)
