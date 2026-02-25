import pandas as pd
import yfinance as yf
import tickers as tk
import numpy as np

### Main functions ###

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
        stock = yf.Ticker(ticker).history(period=period, interval=interval)
        return stock

    elif country is not None:
        if country.upper() in tk.allowed_countries:
            tickers = getattr(tk, country.upper())
            data = {}
            for t in tickers:
                data[t] = yf.Ticker(t).history(period=period, interval=interval)
            return data
        else:
            raise ValueError("Country not supported.")
    if not ticker and not country:
        raise ValueError("Either ticker or country must be provided.")


def cal_yearly_returns(returns:pd.DataFrame):

    """
    Calculates daily returns from stock data.
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

def portfolio_returns(data: dict, keep_pct: float = 0.9) -> pd.DataFrame:
    returns_dict = {}
    lengths = {}

    for ticker, returns_data in data.items():
        #s = returns_data['Close'].pct_change(fill_method=None).dropna()
        #returns_dict[ticker] = s
        #lengths[ticker] = len(s)
        s_log = np.log(returns_data['Close'] / returns_data['Close'].shift(1)).dropna()
        returns_dict[ticker] = s_log
        lengths[ticker] = len(s_log)

    if not returns_dict:
        return pd.DataFrame()

    max_len = max(lengths.values())
    min_len = int(max_len * keep_pct)

    keep = [t for t, n in lengths.items() if n >= min_len]
    returns_dict = {t: returns_dict[t] for t in keep}

    returns_df = pd.concat(returns_dict, axis=1, join="inner").sort_index()

    return returns_df
    '''
    returns = {}

    for ticker in data.keys():
        returns[ticker] = (
            data[ticker]["Close"]
            .pct_change()
            #.dropna()
            .tolist()
        )
    return returns
    '''



### possible later additions ###

def portfolio_value(holdings:dict, stock_data:pd.DataFrame):

    """
    Calculates the total value of a portfolio based on holdings and stock data.
    Args:
        holdings (dict): A dictionary where keys are ticker symbols and values are the number of shares held.
        stock_data (pandas.DataFrame): DataFrame containing historical stock data.
    Returns:
        float: Total value of the portfolio.
    """
    total_value = 0.0
    for ticker, shares in holdings.items():
        if ticker in stock_data.columns.get_level_values(0):
            latest_price = stock_data[ticker]['Close'][-1]
            total_value += latest_price * shares
        else:
            raise ValueError(f"Ticker {ticker} not found in stock data.")
    return total_value







### Old code for reference ###

'''
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
        stock = yf.Ticker(ticker).history(period=period, interval=interval)
        return stock

    elif country is not None:
        if country.upper() in tk.allowed_countries:
            tickers = getattr(tk, country.upper())
            data = yf.Tickers(tickers).history(period=period, interval=interval)
            return data
        else:
            raise ValueError("Country not supported.")
    if not ticker and not country:
        raise ValueError("Either ticker or country must be provided.")
'''