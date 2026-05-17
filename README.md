# Rebalancing a Portfolio

Rebalancing a Portfolio is a Python project for portfolio optimization and portfolio rebalancing. This project is a B.Sc engeneering final project from students at Reykjavík University.

Project Members:

* Auðunn Fannar HafÞórsson
* Birgir Bragi Gunnþórsson
* Finnur H. Finnsson
* Sváfnir Ingi Jónsson

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
## Dependencies

* pandas
* numpy
* matplotlib
* scipy
* yfinance
  
## Run

### Navigate to the project directory

* Mac/Linux
```bash
cd /Users/"Your/Path/To"/VerkX
```
* Windows
```bash
cd C:\Users"\Your\Path\To"\VerkX
```
Note: change the "Your Path To" to match the path on your computer

### Run the main file
  
```bash
python main.py
```

## Goal

The goal of this project is to experiment with portfolio management, efficient frontier analysis, and automated portfolio rebalancing using Python.

## UI

!! Work In Progress !!

As of now the user interface is still a work in progress. We have non the less created a web-app solution for one that is included in this repo.

## To run the UI

### Navigate to the project directory

* Mac/Linux
```bash
cd /Users/"Your/Path/To"/VerkX/UI_Main
```
* Windows
```bash
cd C:\Users"\Your\Path\To"\VerkX\UI_Main
```
Note: change the "Your Path To" to match the path on your computer

### Run

```bash
streamlit run streamlir_app.py
```

Note: This should open up a tab on your default browser to the locally hosted web-app.
