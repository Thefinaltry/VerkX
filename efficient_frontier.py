import numpy as np
import pandas as pd



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

def calculate_min_var(returns:pd.DataFrame, yearly_returns:pd.DataFrame):
    _, cov_inv = get_covariance_matrix(returns)
    ones = pd.Series(1.0, index=cov_inv.index)
    numerator = cov_inv @ ones
    denominator = ones.T @ cov_inv @ ones
    min_var_weights = numerator / denominator

    
    expected_return_of_min_var = yearly_returns.T @ min_var_weights
    std_of_min_var = 1/np.sqrt(denominator)
    return [min_var_weights, expected_return_of_min_var, std_of_min_var]

def calculate_efficient_frontier(returns:pd.DataFrame,yearly_returns:pd.DataFrame):
    cov_annual, cov_inv = get_covariance_matrix(returns)
    _, expected_return_of_min_var, _ = calculate_min_var(returns, yearly_returns)

    ones = pd.Series(1.0, index=cov_inv.index)
    mu = yearly_returns.loc[cov_inv.index]
    denominator = ones.T @ cov_inv @ ones

    target_returns = np.arange(float(expected_return_of_min_var), 0.50 + 1e-12, 0.0025)
    stds = []
    weights = []

    for i in target_returns:
        w = ((i * ((cov_inv @ mu * (denominator))-((cov_inv @ ones) * (ones.T @ cov_inv @ mu)))) + ((cov_inv @ ones) * (mu.T @ cov_inv @ mu)) - ((cov_inv @ mu) * (mu.T @ cov_inv @ ones)))/((denominator * (mu.T @ cov_inv @ mu))-((ones.T @ cov_inv @ mu) * (mu.T @ cov_inv @ ones)))
        weights.append(w)
        std = np.sqrt(w @ cov_annual @ w.T)
        stds.append(std)
    
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
