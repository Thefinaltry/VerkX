import pandas as pd
import yfinance as yf
import tickers as tk
import numpy as np


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
        if country.upper() in tk.allowed_countries:
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
        else:
            raise ValueError("Country not supported.")

    raise ValueError("Either ticker or country must be provided.")

def years_available(prices: pd.DataFrame, periods_per_year: int = 252) -> pd.Series:
    return (prices.notna().sum() - 1) / periods_per_year

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
def get_data_between_dates(ticker: str, start_date, end_date, interval: str = "1d"):
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    data = yf.Ticker(ticker).history(
        start=start_date,
        end=end_date + pd.Timedelta(days=1),
        interval=interval,
        auto_adjust=False,
        actions=True,
        repair=True
    )

    return data


def get_index(start_date,end_date,ticker: str = "^OMXI15"):
    data = get_data_between_dates(ticker=ticker, start_date=start_date, end_date=end_date)
    returns = data["Close"].interpolate(method="linear").pct_change(fill_method=None).dropna()

    expected_return = cal_yearly_returns(returns.to_frame("index"))
    expected_return = float(expected_return.iloc[0])

    std = float(returns.std() * np.sqrt(252))

    return expected_return, std


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