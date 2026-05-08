import efficient_frontier as ef
import get_data as gt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation

def rebalance_through_time(display_graph: bool, returns:pd.DataFrame, ef_returns:pd.DataFrame, current_date: pd.Timestamp, offset: int ,frequency: int, risk = 1, rebalance_distance: int = 0, bounded: bool = False, short_bound: float=None, long_bound: float=None):

    """
    Rebalance the portfolio through time by calculating the minimum variance portfolio at regular intervals and moving forward by x days.
    Parameters:
    returns (pd.DataFrame): A DataFrame of daily returns for each asset.
    current_date (pd.Timestamp): The starting date for rebalancing.
    offset (int): The number of years to look back for calculating the efficient frontier.
    bounded (bool): Whether to use bounded optimization for the minimum variance portfolio (default is False).
    short_bound (float): The upper bound for short positions if bounded optimization is used (default is None).
    long_bound (float): The upper bound for long positions if bounded optimization is used (default is None).
    Returns:
    list_of_expected_returns
    list_of_stds
    list_of_portfolio_values
    list_of_fee_costs
    """

    end_date = returns.index.max()
    list_of_expected_returns = []
    list_of_stds = []
    #list_of_weights = []
    list_of_turnover = []
    list_of_fee_costs = []
    #list_of_period_returns = []
    list_of_portfolio_values = []

    portfolio_value = 1
    list_of_portfolio_returns = [portfolio_value]
    previous_date = current_date
    #fee_rate = 0.0075
    fee_rate = 0.0075

    is_inf = isinstance(rebalance_distance, str) and rebalance_distance.lower() == 'inf'

    if not is_inf:
        rebalance_distance = rebalance_distance/100

    yearly_returns_ef = gt.cal_yearly_returns(ef_returns)

    if risk == 1:
        if display_graph == True:
            if bounded:
                target_returns_ef, stds_ef, weights_ef = ef.calculate_efficient_frontier(ef_returns, yearly_returns_ef, True, short_bound, long_bound)
            else:
                target_returns_ef, stds_ef, weights_ef = ef.calculate_efficient_frontier(ef_returns, yearly_returns_ef, False)
        if bounded:
            min_var_weights, expected_return_of_min_var, std_of_min_var = ef.calculate_min_var(ef_returns,yearly_returns_ef,True,short_bound,long_bound)
        else:
            min_var_weights, expected_return_of_min_var, std_of_min_var = ef.calculate_min_var(ef_returns,yearly_returns_ef,False)
            
        portfolio_weights = min_var_weights
    else:
        if bounded:
            target_returns_ef, stds_ef, weights_ef = ef.calculate_efficient_frontier(ef_returns, yearly_returns_ef, True, short_bound, long_bound)
        else:
            target_returns_ef, stds_ef, weights_ef = ef.calculate_efficient_frontier(ef_returns, yearly_returns_ef, False)
        
        if risk == 'slope':
            x_where_one, y_where_one, weights_where_one = find_derivative(target_returns_ef,stds_ef,weights_ef)
            portfolio_weights = weights_where_one
        else:
            frontier_idx = int(round((risk - 1) / 9 * (len(weights_ef) - 1)))
            portfolio_weights = weights_ef[frontier_idx]
    
    previous_date = current_date
    index = 1
    if display_graph == True:
        plt.ion()
        fig = plt.figure(figsize=(8,5))
    #list_of_weights.append(portfolio_weights.copy())
    while current_date <= end_date:
        #print(current_date)
        ef_start_date = current_date - pd.DateOffset(years=offset)
        ef_start_date = returns.index[returns.index >= ef_start_date][0]

        period_returns = returns.loc[ef_start_date:current_date]
        #period_returns.to_csv("period_returns.csv")
        yearly_returns = gt.cal_yearly_returns(period_returns)

        if risk == 1:
            current_target_weights, current_expected_return_of_target, current_std_of_target = ef.calculate_min_var(period_returns, yearly_returns, bounded, short_bound, long_bound)
            if display_graph == True:
                if bounded:
                    target_returns, stds, weights = ef.calculate_efficient_frontier(period_returns, yearly_returns, True, short_bound, long_bound)
                else:
                    target_returns, stds, weights = ef.calculate_efficient_frontier(period_returns, yearly_returns, False)
        else:
            if bounded:
                target_returns, stds, weights = ef.calculate_efficient_frontier(period_returns, yearly_returns, True, short_bound, long_bound)
            else:
                target_returns, stds, weights = ef.calculate_efficient_frontier(period_returns, yearly_returns, False)
            
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

        cov_annual, cov_inv = ef.get_covariance_matrix(period_returns)
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
            else:
                portfolio_weights = drifted_weights
        else:
            portfolio_weights = drifted_weights

        if len(list_of_portfolio_values) == 0:
            period_return = portfolio_value - 1.0
        else:
            period_return = portfolio_value / list_of_portfolio_values[-1] - 1

        list_of_turnover.append(turnover)
        list_of_fee_costs.append(fee_cost)
        #list_of_period_returns.append(period_return)
        list_of_portfolio_values.append(portfolio_value)
        #list_of_weights.append(portfolio_weights.copy())
        list_of_expected_returns.append(expected_return_of_portfolio)
        list_of_stds.append(std_of_portfolio)
        '''
        dx = abs(current_std_of_target - std_of_portfolio)
        dy = abs(current_expected_return_of_target - expected_return_of_portfolio)
        '''
        #index_expected_return, index_std = gt.get_index(start_date=ef_start_date,end_date=current_date,ticker="^OMXI15")

        if display_graph == True:
            plt.clf()
            plt.plot(stds, target_returns[0:len(stds)])
            plt.plot(current_std_of_target, current_expected_return_of_target, 'ro')
            plt.plot(std_of_portfolio, expected_return_of_portfolio, 'bo')
            #plt.plot(index_std, index_expected_return, 'go', label='OMXI15')

            if not is_inf:
                if expected_return_of_portfolio < current_expected_return_of_target - rebalance_distance or std_of_portfolio > current_std_of_target + rebalance_distance:
                    plt.plot(
                        [current_std_of_target, std_of_portfolio],
                        [current_expected_return_of_target, expected_return_of_portfolio],
                        linestyle=':', color='orange', linewidth=2
                    )

            plt.xlabel("Volatility")
            plt.ylabel("Expected Return")
            plt.title("Efficient Frontier (Íslenski markaðurinn)")
            plt.grid(True)
            plt.show()
            plt.pause(0.3)

        current_date = next_date
        index += 1
    if display_graph == True:
        plt.ioff()
        plt.show()
    return list_of_expected_returns, list_of_stds, list_of_portfolio_values, list_of_fee_costs, list_of_turnover

def is_close(x, values, tol=0.002):
    return any(abs(x - v) <= tol for v in values)

def trace_path(list_of_expected_returns, list_of_stds):
    x = np.array(list_of_stds)
    y = np.array(list_of_expected_returns)

    num_frames = 200

    t = np.linspace(0, len(x)-1, num_frames)

    x_smooth = np.interp(t, np.arange(len(x)), x)
    y_smooth = np.interp(t, np.arange(len(y)), y)

    fig, ax = plt.subplots()

    padding = 0.1
    ax.set_xlim(min(x) - padding, max(x) + padding)
    ax.set_ylim(min(y) - padding, max(y) + padding)

    line, = ax.plot([], [], color='blue', linestyle='--', linewidth=2)
    dot, = ax.plot([], [], 'ro', markersize=8)

    coord_text = ax.text(0, 0, '')

    def init():
        line.set_data([], [])
        dot.set_data([], [])
        coord_text.set_text('')
        return line, dot, coord_text

    def update(frame):
        x_now = x_smooth[frame]
        y_now = y_smooth[frame]

        line.set_data(x_smooth[:frame+1], y_smooth[:frame+1])
        dot.set_data([x_now], [y_now])
        coord_text.set_position((x_now, y_now))
        coord_text.set_text(f'({x_now:.3f}, {y_now:.3f})')
        
        return line, dot, coord_text

    ani = FuncAnimation(
        fig,
        update,
        frames=len(x_smooth),
        init_func=init,
        interval=30,
        blit=True,
        repeat=False
    )

    plt.show()

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