import pandas as pd
import efficient_frontier as ef
import get_data as gt

def rebalance_through_time(returns:pd.DataFrame, current_date: pd.Timestamp, offset: int, bounded: bool = False, short_bound: float=0.15, long_bound: float=0.15):
    end_date = returns.index.max()
    
    while current_date <= end_date:
        print(current_date)
        ef_start_date = current_date - pd.DateOffset(years=offset)
        ef_start_date = returns.index[returns.index >= ef_start_date][0]

        period_returns = returns.loc[ef_start_date:current_date]
        yearly_returns = gt.cal_yearly_returns(period_returns)
        min_var_weights, expected_return_of_min_var, std_of_min_var = ef.calculate_min_var(returns, yearly_returns, bounded, short_bound, long_bound)


        # move forward 6 months
        target_date = current_date + pd.DateOffset(months=6)
    
        idx = returns.index.searchsorted(target_date)
        if idx >= len(returns.index):
            break
        
        current_date = returns.index[idx]

