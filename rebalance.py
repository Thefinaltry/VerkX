import efficient_frontier as ef
import get_data as gt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation

def rebalance_through_time(min_var_weights: pd.Series, returns:pd.DataFrame, current_date: pd.Timestamp, offset: int ,frequency: int, bounded: bool = False, short_bound: float=None, long_bound: float=None):
    end_date = returns.index.max()
    list_of_expected_returns = []
    list_of_stds = []
    list_of_weights = []
    list_of_turnover = []
    list_of_fee_costs = []
    list_of_period_returns = []
    list_of_portfolio_values = []

    portfolio_value = 1
    list_of_portfolio_returns = [portfolio_value]
    previous_date = current_date
    fee_rate = 0.0075
    
    index = 1
    while current_date <= end_date:
        #print(current_date)
        ef_start_date = current_date - pd.DateOffset(years=offset)
        ef_start_date = returns.index[returns.index >= ef_start_date][0]

        period_returns = returns.loc[ef_start_date:current_date]
        #period_returns.to_csv("period_returns.csv")
        yearly_returns = gt.cal_yearly_returns(period_returns)
        current_min_var_weights, current_expected_return_of_min_var, current_std_of_min_var = ef.calculate_min_var(period_returns, yearly_returns, bounded, short_bound, long_bound)
        '''
        if bounded:
            target_returns, stds, weights = ef.calculate_efficient_frontier(period_returns, yearly_returns, True, short_bound, long_bound)
        else:
            target_returns, stds, weights = ef.calculate_efficient_frontier(period_returns, yearly_returns, False)
        '''
            
        cov_annual, cov_inv = ef.get_covariance_matrix(period_returns)
        std_of_min_var = np.sqrt(min_var_weights @ cov_annual @ min_var_weights.T)
        expected_return_of_min_var = yearly_returns.T @ min_var_weights

        if index == 1:
            list_of_weights.append(min_var_weights)
        else:
            realized_window = returns.loc[(returns.index > previous_date) & (returns.index <= current_date)]

            if not realized_window.empty:
                asset_growth = (1 + realized_window).prod()
                pre_rebalance_values = portfolio_value * min_var_weights * asset_growth
                portfolio_value = pre_rebalance_values.sum()
                
                drifted_weights = pre_rebalance_values / portfolio_value
                #print(drifted_weights)
            else:
                drifted_weights = min_var_weights

            # default: no rebalance
            turnover = 0.0
            fee_cost = 0.0

            if expected_return_of_min_var < current_expected_return_of_min_var or std_of_min_var > current_std_of_min_var:
                turnover = np.abs(current_min_var_weights - drifted_weights).sum()
                fee_cost = portfolio_value * fee_rate * turnover
                portfolio_value -= fee_cost

                list_of_weights.append(current_min_var_weights)
                min_var_weights = current_min_var_weights
            else:
                min_var_weights = drifted_weights
            
            if list_of_portfolio_values:
                period_return = portfolio_value / list_of_portfolio_values[-1] - 1
            else:
                period_return = np.nan
            
            list_of_turnover.append(turnover)
            list_of_fee_costs.append(fee_cost)
            list_of_period_returns.append(period_return)
            list_of_portfolio_values.append(portfolio_value)
            list_of_weights.append(min_var_weights.copy())

        list_of_expected_returns.append(expected_return_of_min_var)
        list_of_stds.append(std_of_min_var)

        '''
        plt.figure(figsize=(8,5))
        plt.plot(stds, target_returns[0:len(stds)])
        plt.plot(std_of_min_var, expected_return_of_min_var, 'ro')  # 'r' = red, 'o' = circle
        plt.xlabel("Volatility")
        plt.ylabel("Expected Return")
        plt.title("Efficient Frontier (Íslenski markaðurinn)")
        plt.grid(True)
        plt.show()
        '''

        previous_date = current_date
        
        # move forward x months
        target_date = current_date + pd.DateOffset(days=frequency)
    
        idx = returns.index.searchsorted(target_date)
        if idx >= len(returns.index):
            break
        
        current_date = returns.index[idx]
        index += 1
    return list_of_expected_returns, list_of_stds, list_of_weights, list_of_portfolio_values, list_of_period_returns, list_of_turnover, list_of_fee_costs

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