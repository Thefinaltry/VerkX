# This is the main entry point of the application

import functions as f

data = f.get_data(country='iceland', period='1mo', interval='1d')
print(data)
returns = f.portfolio_returns(data)
print(returns)


