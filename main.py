# This is the main entry point of the application

import get_data as gt


### Testing functions ###
data = gt.get_data(country='iceland', period='1mo', interval='1d')
returns = gt.portfolio_returns(data)

print(returns)


### main application logic would go here ###


def main():
    ...
    pass


