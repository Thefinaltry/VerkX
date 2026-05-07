

FREQUENCY_INFO = """
Frequency means how often the you check if rebalance is needed, in days.\n
For example, if you select 30, the portfolio will be rebalanced every 30 days
if rebalancing conditions are met.\n
Rebalancing conditions are selected here below."""

SAFE_DISTANCE_INFO = """
Distance means percentage distance from the efficient frontier portfolio.\n
Inputs: 1 reprisents 1% distance, 5 represents 5% distance, etc. or "inf" for infinite distance\n
0 means no safe distance -> Portfolio rebalances at set frequency here above.
"""

RISK_TOLERANCE_INFO = """
Risk tolerance means where on the efficient frontier you want to be.\n
Inputs: [From 1 to 10, Integers Only] \n
0 means you want to be on the minimum variance portfolio, 
10 means you want to be on the maximum return portfolio etc.\n 
You can also select "slope" for the point where the slope of the efficient frontier is 1.\n
If you select "slope", the portfolio will be rebalanced to the point on the efficient frontier 
where the slope is 1, which is the point where the portfolio has the best risk-return trade-off.
"""