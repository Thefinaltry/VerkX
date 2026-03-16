import pandas as pd
import yfinance as yf
import tickers as tk
import numpy as np

### Main functions ###
def get_data_chat(ticker=None, country=None, period="max", interval="1d"):
    """
    Fetches (adjusted) price data for a given ticker symbol using yfinance,
    or multiple tickers from tickers.py.

    Returns:
        pd.DataFrame: price matrix with index=Date and columns=tickers.
                      Uses "Adj Close" when available (dividends + splits),
                      otherwise falls back to "Close".
    """

    if ticker is not None:
        tickers = [ticker]

        df = yf.download(
            tickers,
            period=period,
            interval=interval,
            threads=True,
            progress=False,
            auto_adjust=False
        )

        if df.empty:
            raise ValueError("No data returned in tickers, may be ticker / interval / period.")

        # prefer total-return series when available
        col = "Adj Close" if "Adj Close" in df.columns else "Close"
        close_price = df[[col]].rename(columns={col: ticker})

        close_price.columns.name = None
        return close_price.dropna()

    elif country is not None:
        if country.upper() not in tk.allowed_countries:
            raise ValueError("Country not supported.")

        tickers = list(getattr(tk, country.upper()))

        df = yf.download(
            tickers,
            period=period,
            interval=interval,
            threads=True,
            progress=False,
            auto_adjust=False
        )

        if df.empty:
            raise ValueError("No data returned in tickers, may be tickers / interval / period.")

        # If only one ticker, columns are single-level
        if len(tickers) == 1:
            col = "Adj Close" if "Adj Close" in df.columns else "Close"
            close_prices = df[[col]].rename(columns={col: tickers[0]})
        else:
            # MultiIndex columns: (field, ticker)
            field = "Adj Close" if "Adj Close" in df.columns.get_level_values(0) else "Close"
            close_prices = df[field]

        close_prices.columns.name = None
        close_prices = close_prices.dropna(axis=1, how="all")
        return close_prices.dropna(how="all")

    else:
        raise ValueError("Either ticker or country must be provided.")

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

def cagr_over_available(prices: pd.DataFrame, periods_per_year: int = 252, min_periods: int = 60) -> pd.Series:
    """
    Annualized return (CAGR) computed over each ticker's available history
    within the provided prices DataFrame.

    For each ticker, uses first and last non-NaN prices in the window.
    Returns r such that: start * (1+r)^(years_used) = end

    Args:
        prices: DataFrame of prices (index=dates, columns=tickers)
        periods_per_year: 252 for daily, ~52 for weekly
        min_periods: minimum number of price observations required to compute a CAGR

    Returns:
        Series of annualized returns (float) per ticker.
    """
    out = {}

    for t in prices.columns:
        s = prices[t].dropna()
        if len(s) < min_periods:
            continue  # skip too-short histories

        start = s.iloc[0]
        end = s.iloc[-1]
        periods = len(s) - 1
        years_used = periods / periods_per_year

        if years_used <= 0 or start <= 0 or end <= 0:
            continue

        out[t] = (end / start) ** (1 / years_used) - 1

    return pd.Series(out, name="cagr").sort_values(ascending=False)
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