import tickers as tk
import pandas as pd
import yfinance as yf
import numpy as np
import streamlit as st
from scipy.optimize import minimize

def get_data(ticker=None,country=None, period="max", interval="1d"):

    """
    Fetches stock data for a given ticker symbol using yfinance library.
    or multiple tickers from tickers.py.
    Args:
        ticker (str): The stock ticker symbol. e.g., "ARION.IC" for Arion Banki.
        country (str): The country name to fetch multiple tickers. e.g., "iceland".
        period (str): The period for which to fetch data. e.g., "1y", "5d", "2mo", "max".
        interval (str): The data interval. e.g., "1d", "1h", "15m".
    Returns:
        pandas.DataFrame: DataFrame containing historical stock data.
    """

    if ticker is not None:
        return yf.Ticker(ticker).history(
            period=period,
            interval=interval,
            auto_adjust=False,
            actions=True,
            repair=True
        )

    elif country is not None:

        tickers = getattr(tk, country.upper())
        data = {}
        for t in tickers:
            data[t] = yf.Ticker(t).history(
                    period=period,
                    interval=interval,
                    auto_adjust=False,
                    actions=False
                )      
        return data

def load_data(name, period):

    if name == "Iceland":
        country = "iceland"
        data = get_data(country=country, period=str(f'{period}y'))
        return data
    elif name == "Select Custom Portfolio":
        tickers_input = st.text_input(
        "Enter tickers (e.g., AAPL, MSFT, GOOGL). Note: Only Icelandic tickers are supported as of now."
        )
        tickers = [ticker.strip().upper() for ticker in tickers_input.split(",")]
        data = get_data(tickers=tickers, period=str(f'{period}y'))
        return data
    
def get_returns(data: dict, keep_pct: float = 0.9, slice_output: bool = False, ef_period: int = 0) -> pd.DataFrame:
    returns_dict = {}
    lengths = {}

    for ticker, returns_data in data.items():
        s = returns_data['Close'].interpolate(method='linear').pct_change(fill_method=None).dropna() #.ffill()
        returns_dict[ticker] = s
        lengths[ticker] = len(s)

    if not returns_dict:
        return pd.DataFrame()

    max_len = max(lengths.values())
    min_len = int(max_len * keep_pct)

    keep = [t for t, n in lengths.items() if n >= min_len]
    returns_dict = {t: returns_dict[t] for t in keep}

    returns_df = pd.concat(returns_dict, axis=1, join="inner").sort_index()
    #returns_df.to_csv('returns.csv')

    if slice_output:
        start = returns_df.index.min()
        end = start + pd.DateOffset(years=ef_period)
        returns_df_efficient_frontier = returns_df.loc[start:end]
    else:
        returns_df_efficient_frontier = None

    return returns_df, returns_df_efficient_frontier

def cal_yearly_returns(returns:pd.DataFrame):

    """
    Calculates yearly returns from stock data.
    Args:
        stock_data (pandas.DataFrame): DataFrame containing historical stock data.
    
    Returns:
        pandas.Series: Series containing daily returns. 
        First value will be NaN since there is no previous day to compare to,
        there for -> size = len(stock_data) - 1.
    """
    total_return = (1 + returns).prod()
    total_days = returns.shape[0]

    return total_return ** (252 / total_days) - 1

def get_covariance_matrix(returns):

    """
    Calculate the annualized covariance matrix and its inverse from daily returns.
    Parameters:
    returns (pd.DataFrame): A DataFrame of daily returns for each asset.
    Returns:
    cov_annual (pd.DataFrame): The annualized covariance matrix.
    cov_inv (pd.DataFrame): The inverse of the annualized covariance matrix.
    """

    cov_matrix = returns.cov()
    cov_annual = cov_matrix * 252

    try:
        cov_inv_array = np.linalg.inv(cov_annual.values)
    except np.linalg.LinAlgError:
        cov_inv_array = np.linalg.pinv(cov_annual.values)

    cov_inv = pd.DataFrame(
        cov_inv_array,
        index=cov_annual.index,
        columns=cov_annual.columns
    )

    return cov_annual, cov_inv

def calculate_min_var(returns:pd.DataFrame, yearly_returns:pd.DataFrame, bounded: bool = False, short_bound: float = 0.15, long_bound: float = 0.15):

    """
    Calculate the minimum variance portfolio weights and performance metrics.
    Parameters:
    returns (pd.DataFrame): A DataFrame of daily returns for each asset.
    yearly_returns (pd.DataFrame): A DataFrame of yearly returns for each asset.
    bounded (bool): Whether to use bounded optimization.
    short_bound (float): The upper bound for short positions.
    long_bound (float): The upper bound for long positions.
    Returns:
    list: A list containing the minimum variance portfolio weights, expected return, and standard deviation.
    """

    if bounded:
        cov_annual, cov_inv = get_covariance_matrix(returns)
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
        return [min_var_weights, expected_return_of_min_var, std_of_min_var, cov_annual, cov_inv]
    else:
        cov_annual, cov_inv = get_covariance_matrix(returns)
        ones = pd.Series(1.0, index=cov_inv.index)
        numerator = cov_inv @ ones
        denominator = ones.T @ cov_inv @ ones
        min_var_weights = numerator / denominator

        
        expected_return_of_min_var = yearly_returns.T @ min_var_weights
        std_of_min_var = 1/np.sqrt(denominator)
        return [min_var_weights, expected_return_of_min_var, std_of_min_var, cov_annual, cov_inv]

def bounded_portfolio_weights(cov_annual: pd.DataFrame, mu: pd.Series, target_return: float, short_bound: float = 0.15, long_bound: float = 0.15, x0=None) -> pd.Series:

    """
    Calculate portfolio weights for a given target return with bounds on short and long positions.
    Parameters:
    cov_annual (pd.DataFrame): The annualized covariance matrix of asset returns.
    mu (pd.Series): The expected returns of the assets.
    target_return (float): The desired target return for the portfolio.
    short_bound (float): The maximum allowed short position (default is 0.15).
    long_bound (float): The maximum allowed long position (default is 0.15).
    x0 (np.ndarray): Initial guess for the optimization (default is None, which uses an equal-weighted portfolio).
    Returns:
    pd.Series: The optimized portfolio weights that achieve the target return while respecting the bounds.
    """

    n = len(mu)
    if x0 is None:
        x0 = np.ones(n) / n
    bounds = [(-short_bound, long_bound)] * n
    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
        {"type": "eq", "fun": lambda w: mu.values @ w - target_return},
    ]

    result = minimize(fun=lambda w: w @ cov_annual.values @ w, x0=x0, method="SLSQP", bounds=bounds, constraints=constraints, options={"maxiter": 500, "ftol": 1e-6})

    if not result.success:
        return None
        #raise ValueError(f"Optimization failed for target return {target_return:.4f}: {result.message}")

    return pd.Series(result.x, index=mu.index)

def find_derivative(target_returns, stds, weights, target_slope=1.0):

    n = min(len(target_returns), len(stds), len(weights))

    x = np.asarray(stds[:n], dtype=float)
    y = np.asarray(target_returns[:n], dtype=float)
    weights = weights[:n]

    order = np.argsort(x)
    x = x[order]
    y = y[order]
    weights = [weights[i] for i in order]

    dydx = np.gradient(y, x)

    idx = np.argmin(np.abs(dydx - target_slope))

    x_closest = x[idx]
    y_closest = y[idx]
    weights_closest = weights[idx]
    slope_closest = dydx[idx]

    return x_closest, y_closest, weights_closest #, slope_closest

def calculate_efficient_frontier(returns:pd.DataFrame,yearly_returns:pd.DataFrame, bounded: bool = False, short_bound: float = None, long_bound: float = None, risk_tolerance: int = 0):

    """
    Calculate the efficient frontier for a given set of returns and yearly returns, with optional bounds on short and long positions.
    Parameters:
    returns (pd.DataFrame): A DataFrame of daily returns for each asset.
    yearly_returns (pd.DataFrame): A DataFrame of yearly returns for each asset.
    bounded (bool): Whether to use bounded optimization (default is False).
    short_bound (float): The upper bound for short positions (default is None)
    long_bound (float): The upper bound for long positions (default is None).
    Returns:
    tuple: A tuple containing the target returns, standard deviations, and corresponding portfolio weights for the efficient frontier.
    """

    min_var_weights, min_var_expected_return, min_var_stds, cov_annual, cov_inv = calculate_min_var(returns, yearly_returns, bounded, short_bound, long_bound)

    #print(min_var_weights)
    ones = pd.Series(1.0, index=cov_inv.index)
    mu = yearly_returns.loc[cov_inv.index]
    denominator = ones.T @ cov_inv @ ones

    start = float(min_var_expected_return) + 0.0025
    end = start + 0.5 + 1e-12
    target_returns = [min_var_expected_return] + list(np.arange(start, end, 0.0025))
    stds = [min_var_stds]
    weights = [min_var_weights]

    x0 = np.ones(len(mu)) / len(mu)
    for i in target_returns:
        if i == target_returns[0]:
            pass
        else:
            if bounded:
                w = bounded_portfolio_weights(cov_annual, mu, i, short_bound, long_bound, x0)
            else:
                w = ((i * ((cov_inv @ mu * (denominator))-((cov_inv @ ones) * (ones.T @ cov_inv @ mu)))) + ((cov_inv @ ones) * (mu.T @ cov_inv @ mu)) - ((cov_inv @ mu) * (mu.T @ cov_inv @ ones)))/((denominator * (mu.T @ cov_inv @ mu))-((ones.T @ cov_inv @ mu) * (mu.T @ cov_inv @ ones)))
            if w is None:
                break
        
            weights.append(w)
            std = np.sqrt(w @ cov_annual @ w.T)
            stds.append(std)
            x0 = w.values

    if st.session_state.risk_tolerance == 1:

        portfolio_weights = min_var_weights

    else:

        if st.session_state.risk_tolerance == 'slope':
            _, _, weights_where_one = find_derivative(target_returns,stds,weights)
            portfolio_weights = weights_where_one
        else:
            frontier_idx = int(round((int(st.session_state.risk_tolerance) - 1) / 9 * (len(weights) - 1)))
            portfolio_weights = weights[frontier_idx]

    return target_returns, stds, weights, frontier_idx, portfolio_weights

def rebalance_through_time(returns:pd.DataFrame, current_date: pd.Timestamp, offset: int,
                           frequency: int, risk = 1, rebalance_distance: int = 0, bounded: bool = False, 
                           short_bound: float=None, long_bound: float=None, portfolio_weight = None,
                           fee_rate: float = 0.0075
                           ):
 
    end_date = returns.index.max()
    portfolio_value = 1
    list_of_expected_returns = []
    list_of_stds = []
    list_of_weights = [portfolio_weight.copy()]
    list_of_fee_costs = []
    list_of_period_returns = []
    list_of_portfolio_values = [portfolio_value]
    trading_dates = [current_date]
    rebalance_flags = [True]
    portfolio_weights = portfolio_weight
    is_inf = isinstance(rebalance_distance, str) and rebalance_distance.lower() == 'inf'
    if not is_inf:
        rebalance_distance = rebalance_distance/100

    index = 1
    while current_date <= end_date:

        ef_start_date = current_date - pd.DateOffset(years=offset)
        ef_start_date = returns.index[returns.index >= ef_start_date][0]

        period_returns = returns.loc[ef_start_date:current_date]

        yearly_returns = cal_yearly_returns(period_returns)

        if risk == 1:
            current_target_weights, current_expected_return_of_target, current_std_of_target = calculate_min_var(period_returns, yearly_returns, bounded, short_bound, long_bound)
        else:
            if bounded:
                target_returns, stds, weights,_,_ = calculate_efficient_frontier(period_returns, yearly_returns, True, short_bound, long_bound)
            else:
                target_returns, stds, weights,_,_ = calculate_efficient_frontier(period_returns, yearly_returns, False)
            
            if risk == 'slope':
                current_std_of_target, current_expected_return_of_target, current_target_weights = find_derivative(target_returns,stds,weights)
            else:
                frontier_idx = int(round((risk - 1) / 9 * (len(weights) - 1)))

                current_target_weights = weights[frontier_idx]
                current_expected_return_of_target = target_returns[frontier_idx]
                current_std_of_target = stds[frontier_idx]

        target_date = current_date + pd.DateOffset(days=frequency)

        idx = returns.index.searchsorted(target_date)

        if idx >= len(returns.index):
            next_date = returns.index[-1]
        else:
            next_date = returns.index[idx]

        if next_date <= current_date:
            break

        realized_window = returns.loc[(returns.index > current_date) & (returns.index <= next_date)]

        drifted_weights = portfolio_weights.copy()

        for daily_returns in realized_window.to_numpy():
            portfolio_return = drifted_weights @ daily_returns
            portfolio_value = portfolio_value * (1.0 + portfolio_return)

            drifted_weights = drifted_weights * (1.0 + daily_returns) / (1.0 + portfolio_return)

        portfolio_weights = drifted_weights.copy()

        cov_annual, cov_inv = get_covariance_matrix(period_returns)
        std_of_portfolio = np.sqrt(drifted_weights @ cov_annual @ drifted_weights.T)
        expected_return_of_portfolio = yearly_returns.T @ drifted_weights

        turnover = 0.0
        fee_cost = 0.0

        if not is_inf:
            if expected_return_of_portfolio < current_expected_return_of_target - rebalance_distance or std_of_portfolio > current_std_of_target + rebalance_distance:
                turnover = np.abs(current_target_weights - drifted_weights).sum()
                fee_cost = portfolio_value * fee_rate * turnover
                portfolio_value -= fee_cost
                portfolio_weights = current_target_weights.copy()
                rebalance_flags.append(True)
            else:
                portfolio_weights = drifted_weights
                rebalance_flags.append(False)
        else:
            portfolio_weights = drifted_weights
            rebalance_flags.append(False)

        if len(list_of_portfolio_values) == 0:
            period_return = portfolio_value - 1.0
        else:
            period_return = portfolio_value / list_of_portfolio_values[-1] - 1

        #list_of_turnover.append(turnover)
        list_of_fee_costs.append(fee_cost)
        list_of_period_returns.append(period_return)
        list_of_portfolio_values.append(portfolio_value)
        list_of_weights.append(portfolio_weights.copy())
        list_of_expected_returns.append(expected_return_of_portfolio)
        list_of_stds.append(std_of_portfolio)
        #index_expected_return, index_std = gt.get_index(start_date=ef_start_date,end_date=current_date,ticker="^OMXI15")

        trading_dates.append(next_date)

        current_date = next_date
        index += 1
 
    return list_of_expected_returns, list_of_stds, list_of_portfolio_values, list_of_fee_costs, trading_dates, rebalance_flags, list_of_weights