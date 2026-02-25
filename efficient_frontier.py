import numpy as np
import pandas as pd



### Testing functions ###

def get_covariance_matrix(returns):
    return returns.cov()


def minimum_variance_portfolio(cov_matrix:pd.DataFrame):
    
    """
    Calculates the minimum variance portfolio weights.
    Args:
        cov_matrix (pandas.DataFrame): Covariance matrix of asset returns.
    Returns:
        pandas.Series: Portfolio weights for each asset in the minimum variance portfolio.
    """
    
    inv_cov = np.linalg.inv(cov_matrix)
    ones = np.ones(len(cov_matrix))
    
    weights = inv_cov @ ones / (ones.T @ inv_cov @ ones)
    
    return pd.Series(weights, index=cov_matrix.index)

def portfolio_risk(cov_matrix:pd.DataFrame, weights:pd.Series):
    
    """
    Calculates the risk (standard deviation) of a portfolio given its weights and the covariance matrix.
    Args:
        cov_matrix (pandas.DataFrame): Covariance matrix of asset returns.
        weights (pandas.Series): Portfolio weights for each asset.
    Returns:
        float: Risk (standard deviation) of the portfolio.
    """
    
    return (1 / np.sqrt(weights.T @ cov_matrix @ weights))

def expected_return(exp_returns:pd.Series, weights:pd.Series, cov_matrix:pd.DataFrame):
    
    """
    Calculates the expected return of a portfolio given its weights and expected returns of assets.
    Args:
        exp_returns (pandas.Series): Expected returns of assets.
        weights (pandas.Series): Portfolio weights for each asset.
        cov_matrix (pandas.DataFrame): Covariance matrix of asset returns.
    Returns:
        float: Expected return of the portfolio.
    """

    ones = np.ones(len(cov_matrix))
    exp_returns = exp_returns @ np.linalg.inv(cov_matrix) @ ones / (ones.T @ np.linalg.inv(cov_matrix) @ ones)

    return exp_returns


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
