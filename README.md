# VerkX

VerkX is a Python project for portfolio optimization and portfolio rebalancing.

The code:

* Downloads historical stock data
* Calculates returns and portfolio performance
* Generates an efficient frontier
* Finds better asset allocations based on risk/reward
* Calculates how to rebalance a portfolio

## Main Files

```bash
main.py                 # Runs the project
get_data.py             # Downloads market data
efficient_frontier.py   # Portfolio optimization logic
rebalance.py            # Rebalancing calculations
tickers.py              # Stock ticker lists
```

## How It Works

1. Select stock tickers
2. Download historical price data
3. Calculate returns and volatility
4. Generate optimized portfolio weights
5. Compare current allocation vs target allocation
6. Output rebalance suggestions

## Installation

```bash
git clone https://github.com/Thefinaltry/VerkX.git
cd VerkX
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Dependencies

* pandas
* numpy
* matplotlib
* scipy
* yfinance

## Goal

The goal of this project is to experiment with portfolio management, efficient frontier analysis, and automated portfolio rebalancing using Python.


