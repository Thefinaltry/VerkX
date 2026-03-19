import efficient_frontier as ef
import get_data as gt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation


FEE_RATE = 0.0075


def _portfolio_point(weights: pd.Series, cov_annual: pd.DataFrame, yearly_returns: pd.Series):
    std = float(np.sqrt(weights @ cov_annual @ weights.T))
    expected_return = float(yearly_returns.T @ weights)
    return std, expected_return


def _frontier_vol_at_return(frontier_returns, frontier_stds, target_return: float):
    frontier_returns = np.asarray(frontier_returns, dtype=float)
    frontier_stds = np.asarray(frontier_stds, dtype=float)

    if len(frontier_returns) == 0 or len(frontier_stds) == 0:
        return np.nan

    if len(frontier_returns) == 1:
        return float(frontier_stds[0])

    lo = frontier_returns.min()
    hi = frontier_returns.max()
    clipped_target = np.clip(target_return, lo, hi)
    return float(np.interp(clipped_target, frontier_returns, frontier_stds))


def rebalance_through_time(
    min_var_weights: pd.Series,
    returns: pd.DataFrame,
    current_date: pd.Timestamp,
    offset: int,
    frequency: int,
    bounded: bool = False,
    short_bound: float = None,
    long_bound: float = None,
):
    """
    Simulates portfolio drift and rebalancing through time.

    Returns a DataFrame with one row per rebalance observation. Each row stores:
    - the rolling efficient frontier on that date
    - the drifted portfolio point before rebalance
    - the post-rebalance portfolio point
    - turnover, fee cost, portfolio value, and whether a rebalance occurred
    """
    end_date = returns.index.max()
    portfolio_value = 1.0
    previous_date = current_date
    current_weights = min_var_weights.copy()

    rows = []

    while current_date <= end_date:
        ef_start_date = current_date - pd.DateOffset(years=offset)
        ef_start_date = returns.index[returns.index >= ef_start_date][0]

        period_returns = returns.loc[ef_start_date:current_date]
        yearly_returns = gt.cal_yearly_returns(period_returns)
        cov_annual, _ = ef.get_covariance_matrix(period_returns)

        frontier_returns, frontier_stds, frontier_weights = ef.calculate_efficient_frontier(
            period_returns,
            yearly_returns,
            bounded,
            short_bound,
            long_bound,
        )
        frontier_returns = np.asarray(frontier_returns[: len(frontier_stds)], dtype=float)
        frontier_stds = np.asarray(frontier_stds, dtype=float)

        target_weights, frontier_min_return, frontier_min_std = ef.calculate_min_var(
            period_returns,
            yearly_returns,
            bounded,
            short_bound,
            long_bound,
        )
        target_weights = target_weights.copy()

        if rows:
            realized_window = returns.loc[(returns.index > previous_date) & (returns.index <= current_date)]

            if not realized_window.empty:
                asset_growth = (1 + realized_window).prod()
                pre_rebalance_values = portfolio_value * current_weights * asset_growth
                portfolio_value = float(pre_rebalance_values.sum())
                drifted_weights = (pre_rebalance_values / portfolio_value).copy()
            else:
                drifted_weights = current_weights.copy()
        else:
            drifted_weights = current_weights.copy()

        drifted_std, drifted_return = _portfolio_point(drifted_weights, cov_annual, yearly_returns)

        rebalance_now = False
        turnover = 0.0
        fee_cost = 0.0

        # Keep the original decision rule: rebalance when the current rolling
        # min-var portfolio has a higher expected return than the drifted one.
        if float(frontier_min_return) > drifted_return or frontier_min_std < drifted_std:
            rebalance_now = True
            turnover = float(np.abs(target_weights - drifted_weights).sum())
            fee_cost = portfolio_value * FEE_RATE * turnover
            portfolio_value -= fee_cost
            post_weights = target_weights.copy()
        else:
            post_weights = drifted_weights.copy()

        post_std, post_return = _portfolio_point(post_weights, cov_annual, yearly_returns)
        frontier_std_at_drifted_return = _frontier_vol_at_return(frontier_returns, frontier_stds, drifted_return)
        inefficiency_gap = drifted_std - frontier_std_at_drifted_return

        period_return = np.nan if not rows else portfolio_value / rows[-1]["portfolio_value"] - 1

        rows.append(
            {
                "date": current_date,
                "frontier_returns": frontier_returns.tolist(),
                "frontier_stds": frontier_stds.tolist(),
                "frontier_weights": [w.tolist() if hasattr(w, "tolist") else list(w) for w in frontier_weights],
                "drifted_return": drifted_return,
                "drifted_std": drifted_std,
                "post_return": post_return,
                "post_std": post_std,
                "frontier_min_return": float(frontier_min_return),
                "frontier_min_std": float(frontier_min_std),
                "frontier_std_at_drifted_return": frontier_std_at_drifted_return,
                "inefficiency_gap": inefficiency_gap,
                "turnover": turnover,
                "fee_cost": fee_cost,
                "portfolio_value": portfolio_value,
                "period_return": period_return,
                "rebalanced": rebalance_now,
                "drifted_weights": drifted_weights.to_dict(),
                "post_weights": post_weights.to_dict(),
            }
        )

        current_weights = post_weights.copy()
        previous_date = current_date

        target_date = current_date + pd.DateOffset(days=frequency)
        idx = returns.index.searchsorted(target_date)
        if idx >= len(returns.index):
            break
        current_date = returns.index[idx]

    return pd.DataFrame(rows)



def plot_rebalance_snapshot(history: pd.DataFrame, step: int = -1):
    """Static chart for one rebalance date."""
    if history.empty:
        raise ValueError("history is empty")

    row = history.iloc[step]
    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(row["frontier_stds"], row["frontier_returns"], linewidth=2, label="Efficient frontier")
    ax.scatter(row["drifted_std"], row["drifted_return"], s=80, label="Before rebalance")
    ax.scatter(row["post_std"], row["post_return"], s=80, label="After rebalance")
    ax.plot(
        [row["drifted_std"], row["post_std"]],
        [row["drifted_return"], row["post_return"]],
        linestyle="--",
        linewidth=1.5,
        label="Rebalance move",
    )

    title = pd.to_datetime(row["date"]).strftime("%Y-%m-%d")
    ax.set_title(f"Portfolio vs efficient frontier on {title}")
    ax.set_xlabel("Volatility")
    ax.set_ylabel("Expected return")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.show()



def animate_rebalancing(history: pd.DataFrame):
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    fig, ax = plt.subplots(figsize=(9, 6))

    def _flatten(values):
        out = []
        for v in values.dropna():
            if isinstance(v, (list, tuple, np.ndarray)):
                out.extend(list(v))
        return out

    all_frontier_stds = _flatten(history["frontier_stds"])
    all_frontier_returns = _flatten(history["frontier_returns"])

    all_x = all_frontier_stds + history["drifted_std"].dropna().tolist() + history["post_std"].dropna().tolist()
    all_y = all_frontier_returns + history["drifted_return"].dropna().tolist() + history["post_return"].dropna().tolist()

    if not all_x or not all_y:
        raise ValueError("History does not contain enough data to animate.")

    x_pad = max((max(all_x) - min(all_x)) * 0.08, 0.01)
    y_pad = max((max(all_y) - min(all_y)) * 0.08, 0.01)

    ax.set_xlim(min(all_x) - x_pad, max(all_x) + x_pad)
    ax.set_ylim(min(all_y) - y_pad, max(all_y) + y_pad)
    ax.set_xlabel("Volatility")
    ax.set_ylabel("Expected Return")
    ax.set_title("Portfolio Drift and Rebalancing vs Efficient Frontier")
    ax.grid(True)

    frontier_line, = ax.plot([], [], linewidth=2, label="Efficient frontier")
    drifted_dot, = ax.plot([], [], "o", markersize=8, label="Before rebalance")
    post_dot, = ax.plot([], [], "o", markersize=8, label="After rebalance")
    move_line, = ax.plot([], [], "--", linewidth=1.5, label="Rebalance move")

    info_text = ax.text(
        0.02, 0.98, "",
        transform=ax.transAxes,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
    )

    ax.legend(loc="best")

    def init():
        frontier_line.set_data([], [])
        drifted_dot.set_data([], [])
        post_dot.set_data([], [])
        move_line.set_data([], [])
        info_text.set_text("")
        return frontier_line, drifted_dot, post_dot, move_line, info_text

    def update(frame):
        row = history.iloc[frame]

        frontier_stds = row["frontier_stds"]
        frontier_returns = row["frontier_returns"]

        frontier_line.set_data(frontier_stds, frontier_returns)

        drifted_x = row["drifted_std"]
        drifted_y = row["drifted_return"]
        post_x = row["post_std"]
        post_y = row["post_return"]

        drifted_dot.set_data([drifted_x], [drifted_y])
        post_dot.set_data([post_x], [post_y])
        move_line.set_data([drifted_x, post_x], [drifted_y, post_y])

        date_str = row["date"].strftime("%Y-%m-%d") if hasattr(row["date"], "strftime") else str(row["date"])
        rebalanced = row.get("rebalanced", False)
        turnover = row.get("turnover", 0.0)
        fee_cost = row.get("fee_cost", 0.0)
        gap = row.get("inefficiency_gap", np.nan)

        info_text.set_text(
            f"Date: {date_str}\n"
            f"Rebalanced: {rebalanced}\n"
            f"Turnover: {turnover:.4f}\n"
            f"Fee cost: {fee_cost:.6f}\n"
            f"Gap to frontier: {gap:.4f}"
        )

        return frontier_line, drifted_dot, post_dot, move_line, info_text

    anim = FuncAnimation(
        fig,
        update,
        frames=len(history),
        init_func=init,
        interval=700,
        blit=True,
        repeat=False
    )

    plt.show()
    return anim



def plot_frontier_gap(history: pd.DataFrame):
    """Time series of how far the drifted portfolio sits from the frontier."""
    if history.empty:
        raise ValueError("history is empty")

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(history["date"], history["inefficiency_gap"], linewidth=2)
    ax.axhline(0.0, linestyle="--", linewidth=1)
    ax.set_title("Portfolio volatility gap to the efficient frontier")
    ax.set_xlabel("Date")
    ax.set_ylabel("Extra volatility at same expected return")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
