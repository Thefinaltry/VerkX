# This is the main entry point of the application

import functions as f


### Testing functions ###
data = f.get_data(country='iceland', period='1mo', interval='1d')
returns = f.portfolio_returns(data)

print(returns)


### main application logic would go here ###


def main():
    ...
    pass


