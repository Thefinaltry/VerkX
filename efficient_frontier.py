import numpy as np
import pandas as pd



### Testing functions ###

def get_covariance_matrix(returns):
    return None


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
