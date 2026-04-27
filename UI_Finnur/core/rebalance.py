import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from core import get_data as gt
from core import efficient_frontier as ef


def rebalance_engine(
    returns: pd.DataFrame,
    ef_returns: pd.DataFrame,
    current_date: pd.Timestamp,
    offset: int,
    frequency: int,
    risk=1,
    rebalance_distance=0,
    bounded=False,
    short_bound=None,
    long_bound=None
):
    end_date = returns.index.max()

    portfolio_value = 1.0
    portfolio_weights = None

    results = {
        "stds": [],
        "exp_returns": [],
        "values": [],
        "fees": []
    }

    yearly_returns_ef = gt.cal_yearly_returns(ef_returns)

    # --- initial portfolio ---
    if risk == 1:
        portfolio_weights, _, _ = ef.calculate_min_var(
            ef_returns, yearly_returns_ef, bounded, short_bound, long_bound
        )
    else:
        target_returns, stds, weights = ef.calculate_efficient_frontier(
            ef_returns, yearly_returns_ef, bounded, short_bound, long_bound
        )
        idx = int((risk - 1) / 9 * (len(weights) - 1))
        portfolio_weights = weights[idx]

    fee_rate = 0.0075

    while current_date <= end_date:

        ef_start = current_date - pd.DateOffset(years=offset)
        ef_start = returns.index[returns.index >= ef_start][0]

        window = returns.loc[ef_start:current_date]
        yearly_returns = gt.cal_yearly_returns(window)

        # --- target portfolio ---
        if risk == 1:
            target_w, target_ret, target_std = ef.calculate_min_var(
                window, yearly_returns, bounded, short_bound, long_bound
            )
        else:
            target_returns, stds, weights = ef.calculate_efficient_frontier(
                window, yearly_returns, bounded, short_bound, long_bound
            )
            idx = int((risk - 1) / 9 * (len(weights) - 1))
            target_w = weights[idx]
            target_ret = target_returns[idx]
            target_std = stds[idx]

        # Ensure scalars for comparison
        target_ret = float(target_ret)
        target_std = float(target_std)

        # --- next step ---
        next_date = current_date + pd.DateOffset(days=frequency)
        idx = returns.index.searchsorted(next_date)

        if idx >= len(returns.index):
            next_date = returns.index[-1]
        else:
            next_date = returns.index[idx]

        if next_date <= current_date:
            break

        realized = returns.loc[(returns.index > current_date) & (returns.index <= next_date)]

        drift = portfolio_weights.copy()

        for r in realized.to_numpy():
            pr = drift @ r
            portfolio_value *= (1 + pr)
            drift = drift * (1 + r) / (1 + pr)

        portfolio_weights = drift.copy()

        cov, _ = ef.get_covariance_matrix(window)
        std = float(np.sqrt(drift @ cov @ drift.T))
        exp_ret = float(yearly_returns.T @ drift)  # ensure scalar for comparison

        # --- rebalancing condition ---
        fee = 0.0

        if rebalance_distance != float("inf"):
            if (
                exp_ret < target_ret - rebalance_distance or
                std > target_std + rebalance_distance
            ):
                turnover = np.abs(target_w - drift).sum()
                fee = portfolio_value * fee_rate * turnover
                portfolio_value -= fee
                portfolio_weights = target_w.copy()

        # --- store ---
        results["stds"].append(std)
        results["exp_returns"].append(exp_ret)
        results["values"].append(portfolio_value)
        results["fees"].append(fee)

        current_date = next_date

    return results
