
import yfinance as yf
import tickers as tk

def data_fetcher(ticker, period, interval):

    """
    Fetches stock data for a given ticker symbol using yfinance library.
    Args:
        ticker (str): The stock ticker symbol.
    Returns:
        pandas.DataFrame: DataFrame containing historical stock data.
    """

    stock = yf.Ticker(ticker).history(period=period, interval=interval)

    return stock

def market_data_fetcher(market, period="max", interval="1d"):

    """
    Fetches market data from a given market.
        market (str): The market identifier -> "ICELAND"... etc
        !! Currently only "ICELAND" is supported !!

    Uses data_fetcher() to get the individual stock data.

    Returns: dict : { ticker1: data1, ticker2: data2, ... }
        data{x} -> pandas.DataFrame: DataFrame containing historical stock data.
        
    """

    data = {}
    for ticker in getattr(tk, market):
        data[ticker] = data_fetcher(ticker, period=period, interval=interval)

    return data



