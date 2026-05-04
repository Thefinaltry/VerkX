import get_data as gt
import efficient_frontier as ef
import rebalance as rb
import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import math
import tickers as tk

pd.options.display.float_format = '{:.6f}'.format

warnings.filterwarnings(
    "ignore",
    message="Values in x were outside bounds during a minimize step",
    category=RuntimeWarning
)

### main application logic would go here ###

def fetch_from_user(slice_output: bool = False, rebalance: bool = False):
    period = 0
    efficient_frontier_period = 0
    short_bound = None
    long_bound = None
    while True:
        try:
            period = int(input('Total time period (years): '))
            if period <= 1:
                print("Period must be greater than 1.")
                print()
                continue
            break
        except ValueError:
            print("Invalid input... Please enter an integer.")
            print()
    
    if slice_output:
        while True:
            try:
                efficient_frontier_period = int(input('Number of years to calculate efficient frontier (years): '))
                
                if 1 <= efficient_frontier_period <= period - 1:
                    break
                else:
                    print(f"Invalid time period... Must be a number between 1-{period-1}")
            except ValueError:
                print("Invalid input... Please enter an integer.")
    else:
        efficient_frontier_period = 0

    while True:
        try:
            bounds = input('Limit position size? (y/n): ')
            if bounds.lower() not in ['y', 'n']:
                print("Invalid input... Please enter y or n (yes or no)")
                print()
                continue
            if bounds.lower() == 'y':
                while True:
                    try:
                        short_bound = input("How large can SHORT positions get (%)?: ")
                        if short_bound.lower() in ["inf", 'infinite', 'max', 'unbound']:
                            short_bound = None
                        else:    
                            short_bound = int(short_bound)
                            if short_bound <= 0:
                                short_bound = -1*short_bound
                        while True:
                            try:
                                long_bound = input("How large can LONG positions get (%)?: ")
                                if long_bound.lower() in ["inf", 'infinite', 'max', 'unbound']:
                                    long_bound = None
                                else:    
                                    long_bound = int(long_bound)
                                    if long_bound <= 0:
                                        print("Invalid input... long positions can not be negative (or zero)")
                                        print()
                                        continue
                                break
                            except ValueError:
                                print("Invalid input... Please enter an integer")
                                print()
                        break
                    except ValueError:
                        print("Invalid input... Please enter an integer")
                        print()
            break
        except ValueError:
            print("Invalid input... Please enter y or n (yes or no)")
            print()
    
    if rebalance:
        while True:
            try:
                risk = input('How much risk to take? (1-10 or \'slope\'): ')
                
                if risk.lower() == 'slope':
                    break
                
                risk = int(risk)

                if 1 <= risk <= 10:
                    break
                else:
                    print(f"Invalid time period... Must be a number between 1-10")
                    
            except ValueError:
                print("Invalid input... Please enter an integer.")
        
        while True:
            try:
                rebalance_distance = input('How many % points away from efficient frontier to rebalance portfolio? (0-inf): ')

                if rebalance_distance == 'inf':
                    break

                rebalance_distance = int(rebalance_distance)
                
                if rebalance_distance < 0:
                    print("Invalid input... Distance from efficient frontier can not be negative")
                    print()
                    continue
                
                break

            except ValueError:
                print("Invalid input... Please enter an integer.")

        while True:
            try:
                frequency = int(input('How often to rebalance? (days): '))
                
                if 1 <= frequency <= (period - efficient_frontier_period)*252*0.5:
                    break
                else:
                    print(f"Invalid amount of days... Must be a number between 1-{(period - efficient_frontier_period)*252*0.5} days (maximum half the entire period)")
            except ValueError:
                print("Invalid input... Please enter an integer.")
        
        while True:
            try:
                display_graph = input('Display animation showing every rebalancing step? (y/n): ')
                if display_graph.lower() not in ['y', 'n']:
                    print("Invalid input... Please enter y or n (yes or no)")
                    print()
                    continue
                if display_graph.lower() == 'y':
                    display_graph = True
                    break
                if display_graph.lower() == 'n':
                    display_graph = False
                    break
            except ValueError:
                print("Invalid input... Please enter y or n (yes or no)")
                print()
    
    if short_bound is not None:
        short_bound = float(short_bound)/100
    if long_bound is not None:
        long_bound = float(long_bound)/100

    if rebalance:
        if isinstance(risk, str):
            return period, efficient_frontier_period, short_bound, long_bound, frequency, risk.lower(), rebalance_distance, display_graph
        else:
            return period, efficient_frontier_period, short_bound, long_bound, frequency, risk, rebalance_distance, display_graph
    else:
        return period, efficient_frontier_period, short_bound, long_bound

def menu():
    while True:
        print("\n------ Efficient frontier (Iceland) ------")
        print("1. Plot efficient frontier")
        print("2. Calculate minimum variance portfolio")
        print("3. Test minimum variance porftolio performance")
        print("4. Test rebalancing strategy")
        print("5. Optimize rebalancing strategy")
        print("6. Run 1/N simulation")
        print("7. exit")

        choice = input("Choose an option (1-7): ")

        if choice in ["1", "2", "3", "4", "5", "6", "7"]:
            return int(choice)
        else:
            print("Invalid choice. Please select a number between 1 and 7.")

def get_surviving_tickers_string(period, country='iceland', keep_pct=0.9, interval='1d'):
    period_string = str(period) + 'y'

    data = gt.get_data(
        country=country,
        period=period_string,
        interval=interval
    )

    returns, _ = gt.get_returns(data, keep_pct=keep_pct)

    if returns.empty or len(returns.columns) == 0:
        return ""

    return ",".join(returns.columns)

def fetch_data_for_tickers(period_string, interval='1d',ask_for_input=True, period=10):
    while True:
        if ask_for_input:
            print()
            print("Ticker selection:")
            print("1. Let computer decide")
            print("2. Enter tickers manually")

            choice = input("Choose an option (1-2): ")

            if choice == "1":
                while True:
                    country = input("Which market? (iceland/usa): ").strip().upper()

                    if country in tk.allowed_countries:
                        return gt.get_data(
                            country=country,
                            period=period_string,
                            interval=interval
                        )
                    else:
                        print(f"Invalid market. Choose one of: {tk.allowed_countries}")
                        print()

            elif choice == "2":
                raw_tickers = input("Enter tickers separated by commas: ")

                ticker_list = [
                    ticker.strip().upper()
                    for ticker in raw_tickers.split(",")
                    if ticker.strip()
                ]

                if len(ticker_list) == 0:
                    print("You must enter at least one ticker.")
                    print()
                    continue
            else:
                print("Invalid choice. Please choose 1 or 2.")
                print()
                continue
        else:
            raw_tickers = get_surviving_tickers_string(period=period)
            ticker_list = [
                    ticker.strip().upper()
                    for ticker in raw_tickers.split(",")
                    if ticker.strip()
                ]


        data = {}

        for ticker in ticker_list:
            try:
                ticker_data = gt.get_data(
                    ticker=ticker,
                    period=period_string,
                    interval=interval
                )

                if ticker_data.empty:
                    print(f"Warning: no data found for {ticker}, skipping it.")
                else:
                    data[ticker] = ticker_data

            except Exception as e:
                print(f"Warning: could not fetch {ticker}, skipping it.")
                print(e)

        if len(data) == 0:
            print("No valid ticker data was found. Try again.")
            print()
            continue

        return data

def simulate_one_over_n(simulation_period = 8, period = 10, ask_for_input = True):
            if ask_for_input == True:
                while True:
                    try:
                        simulation_period = int(input('Total time period (years): '))
                        if simulation_period <= 1:
                            print("Period must be greater than 1.")
                            print()
                            continue
                        break
                    except ValueError:
                        print("Invalid input... Please enter an integer.")
                        print()
            else:
                simulation_period = simulation_period

            period_string = str(simulation_period) + 'y'

            if ask_for_input == True:
                data = fetch_data_for_tickers(period_string, interval='1d')
            else:
                data = fetch_data_for_tickers(period_string, interval='1d',ask_for_input=False,period=period)
            returns, _ = gt.get_returns(data, keep_pct=0.9)

            tickers = returns.columns
            starting_weights = pd.Series(1.0 / len(tickers), index=tickers)

            asset_growth = (1.0 + returns).cumprod()
            portfolio_values = asset_growth @ starting_weights

            ending_value = float(portfolio_values.iloc[-1])
            total_return = ending_value - 1.0

            actual_years = returns.shape[0] / 252
            annualized_return = math.exp(math.log(ending_value) / actual_years) - 1

            if ask_for_input == True:
                print()
                print(f"1/N simulation over {period} trading years")
                print(f"Period measured: {returns.index.min().strftime('%Y-%m-%d')} to {returns.index.max().strftime('%Y-%m-%d')}")
                print(f"Stocks that survived data cleaning ({len(tickers)}):")
                print(list(tickers))
                print()
                print(f"Total return: {total_return*100:.2f}%")
                print(f"Annualized return: {annualized_return*100:.2f}%")
            else:
                return total_return, annualized_return
def main():
    while True:
        choice = menu()

        if choice == 1:
            period, _, short_bound, long_bound = fetch_from_user()
            period_string = str(period)+'y'
            data = gt.get_data(country='iceland', period=period_string, interval='1d')
            returns,_ = gt.get_returns(data)
            yearly_returns = gt.cal_yearly_returns(returns)
            if short_bound != None or long_bound != None:
                target_returns, stds, weights = ef.calculate_efficient_frontier(returns,yearly_returns,True,short_bound,long_bound)
            else:
                target_returns, stds, weights = ef.calculate_efficient_frontier(returns,yearly_returns,False)
            plt.figure(figsize=(8,5))
            plt.plot(stds, target_returns[0:len(stds)])
            plt.xlabel("Volatility")
            plt.ylabel("Expected Return")
            plt.title("Efficient Frontier (Íslenski markaðurinn)")
            plt.grid(True)
            plt.show()

        if choice == 2:
            period, _, short_bound, long_bound = fetch_from_user()
            period_string = str(period)+'y'
            data = gt.get_data(country='iceland', period=period_string, interval='1d')
            returns,_ = gt.get_returns(data)
            yearly_returns = gt.cal_yearly_returns(returns)
            if short_bound != None or long_bound != None:
                min_var_weights, expected_return_of_min_var, std_of_min_var = ef.calculate_min_var(returns,yearly_returns,True,short_bound,long_bound)
            else:
                min_var_weights, expected_return_of_min_var, std_of_min_var = ef.calculate_min_var(returns,yearly_returns,False)
            print("Min-var porftolio weights:")
            print(min_var_weights)
            print('Expected return:', expected_return_of_min_var)
            print('Volatility:', std_of_min_var)
            print()

        if choice == 3:
        ### Testing functions ###
            period, ef_period, short_bound, long_bound = fetch_from_user(True)
            period_string = str(period)+'y'

            data = gt.get_data(country='iceland', period=period_string, interval='1d')
            _,ef_returns = gt.get_returns(data,keep_pct=0.9,slice_output=True,ef_period=ef_period)
            returns,_ = gt.get_returns(data)
            
            yearly_returns_ef = gt.cal_yearly_returns(ef_returns)
            
            if short_bound != None or long_bound != None:
                target_returns, stds, weights = ef.calculate_efficient_frontier(ef_returns,yearly_returns_ef, True, short_bound, long_bound)
                min_var_weights,expected_return_of_min_var, std_of_min_var = ef.calculate_min_var(ef_returns,yearly_returns_ef, True, short_bound, long_bound)
            else:
                target_returns, stds, weights = ef.calculate_efficient_frontier(ef_returns,yearly_returns_ef, False)
                min_var_weights,expected_return_of_min_var, std_of_min_var = ef.calculate_min_var(ef_returns,yearly_returns_ef, False)  
            
            annual_return_of_min_var, first, start_date, end_date = ef.return_of_min_var(returns,period,ef_period,min_var_weights)
            print()
            print(f"A {ef_period} year period was used to calculate the min-var portfolio ({first.strftime('%Y-%m-%d')} to {start_date.strftime('%Y-%m-%d')}). The weights are:")
            print(min_var_weights)
            print()
            print(f"Then performance of that portfolio was measured for a {period-ef_period} year period ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
            print(f"It's average annual performance was: {annual_return_of_min_var*100:.2f}% per year")
            print()
        
        if choice == 4:
            period, ef_period, short_bound, long_bound, frequency, risk, rebalance_distance, display_graph = fetch_from_user(True, True)
            period_string = str(period)+'y'
            data = gt.get_data(country='iceland', period=period_string, interval='1d')
            returns,ef_returns = gt.get_returns(data,keep_pct=0.9,slice_output=True,ef_period=ef_period)
            yearly_returns_ef = gt.cal_yearly_returns(ef_returns)
            return_list = []
            parameter_list = []

            #if risk == 1:
            starting_date = returns.index.min() + pd.DateOffset(years=ef_period)
            starting_date = returns.index[returns.index > starting_date][0]           
            end_date = returns.index.max()
            #print(starting_date, end_date)
        
            if short_bound != None or long_bound != None:
                list_of_expected_returns, list_of_stds, list_of_portfolio_values, list_of_fee_costs = rb.rebalance_through_time(display_graph, returns, ef_returns, starting_date, ef_period, frequency, risk, rebalance_distance, True, short_bound, long_bound)
            else:
                list_of_expected_returns, list_of_stds, list_of_portfolio_values, list_of_fee_costs = rb.rebalance_through_time(display_graph, returns, ef_returns, starting_date, ef_period, frequency, risk, rebalance_distance, False)

            #print(list_of_portfolio_values)
            print()
            '''
            if frequency >= 30:
                print("Year by year performance:")
                prev = 1
                indexx = 1
                for i in range(len(list_of_portfolio_values)):
                    if (i+1)%(12//(frequency//30)) == 0 or i==len(list_of_portfolio_values)-1:
                        print(f"year {indexx}: {((list_of_portfolio_values[i]-prev)/prev)*100:.2f}%")
                        indexx += 1
                        prev = list_of_portfolio_values[i]
            else:
                print("Year by year performance:")
                print(len(list_of_portfolio_values))
                print((period-ef_period-1))
                prev = 1
                indexx = 1
                for i in range(len(list_of_portfolio_values)):
                    if (i+1)%(len(list_of_portfolio_values)//(period-ef_period)) == 0 or i==len(list_of_portfolio_values)-1:
                        print(f"year {indexx}: {((list_of_portfolio_values[i]-prev)/prev)*100:.2f}%")
                        indexx += 1
                        prev = list_of_portfolio_values[i]
            '''
            total_return = list_of_portfolio_values[-1] - 1
            annual_return_of_portfolio = math.exp((math.log(total_return+1))/(period-ef_period))-1
            return_list.append(annual_return_of_portfolio)
            parameter_list.append([frequency, rebalance_distance])

            print(f"Total return: {total_return*100:.2f}%")
            print(f"Annualized return: {annual_return_of_portfolio*100:.2f}%")
            print(f"Total trading fees paid: {sum(list_of_fee_costs)*100:.2f}%")

            #rb.trace_path(list_of_expected_returns, list_of_stds)

            #history = rbu.rebalance_through_time(min_var_weights, returns, starting_date, ef_period, frequency, False, short_bound is not None or long_bound is not None, short_bound, long_bound,store_frontier=True)
            #rbu.plot_rebalance_snapshot(history, step=-1)   # latest snapshot
            #rbu.plot_frontier_gap(history)                  # time-series of drift from frontier
            #anim = rbu.animate_rebalancing(history)
        if choice == 5:
            #period, ef_period, short_bound, long_bound, frequency, risk, rebalance_distance, display_graph = fetch_from_user(True, True)
            return_list = []
            parameter_list = []
            strategy_return_list = []
            no_rebalance_difference_list = []
            period = 10
            period_string = str(period)+'y'
            ef_period = 2
            short_bound = None
            long_bound = None
            frequency_list = [i for i in range(1,1080+1,1)]
            risk = 6
            rebalance_distance_list = ['inf',0] #0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.10
            display_graph = False

            counter = 0
            nr_of_runs = ((len(rebalance_distance_list)-1)*len(frequency_list))+1
            _,annualized_return_of_one_over_n = simulate_one_over_n(simulation_period=(period-ef_period),period=period,ask_for_input=False)

            data = gt.get_data(country='iceland', period=period_string, interval='1d')
            returns,ef_returns = gt.get_returns(data,keep_pct=0.9,slice_output=True,ef_period=ef_period)
            yearly_returns_ef = gt.cal_yearly_returns(ef_returns)

            for j in frequency_list:
                frequency = j
                for i in rebalance_distance_list:
                    rebalance_distance = i
                    if rebalance_distance == 'inf':
                        if counter != 0:
                            continue
                    else:
                        rebalance_distance = i*100

                    #if risk == 1:
                    starting_date = returns.index.min() + pd.DateOffset(years=ef_period)
                    starting_date = returns.index[returns.index > starting_date][0]           
                    end_date = returns.index.max()
                    #print(starting_date, end_date)
                
                    if short_bound != None or long_bound != None:
                        list_of_expected_returns, list_of_stds, list_of_portfolio_values, list_of_fee_costs = rb.rebalance_through_time(display_graph, returns, ef_returns, starting_date, ef_period, frequency, risk, rebalance_distance, True, short_bound, long_bound)
                    else:
                        list_of_expected_returns, list_of_stds, list_of_portfolio_values, list_of_fee_costs = rb.rebalance_through_time(display_graph, returns, ef_returns, starting_date, ef_period, frequency, risk, rebalance_distance, False)

                    #print(list_of_portfolio_values)
                    print()
                    total_return = list_of_portfolio_values[-1] - 1
                    annual_return_of_portfolio = math.exp((math.log(total_return+1))/(period-ef_period))-1
                    return_list.append(annual_return_of_portfolio)
                    if rebalance_distance == 'inf':
                        parameter_list.append([frequency, 'inf'])
                    else:
                        parameter_list.append([frequency, rebalance_distance / 100])

                    counter +=1
                    print(f"{counter}/{nr_of_runs}")
                    print(f"Total return: {total_return*100:.2f}%")
                    print(f"Annualized return: {annual_return_of_portfolio*100:.2f}%")
                    print(f"Total trading fees paid: {sum(list_of_fee_costs)*100:.2f}%")
                    
                    if rebalance_distance != 'inf':
                        strategy_return_list.append(annual_return_of_portfolio)
                        no_rebalance_difference_list.append(annual_return_of_portfolio-return_list[0])

            labels = []

            for frequency, rebalance_distance in parameter_list:
                if rebalance_distance == 'inf':
                    continue

                labels.append(f"{frequency}d, {rebalance_distance*100:.0f}%")

            x = np.arange(len(strategy_return_list))

            plt.figure(figsize=(14, 6))
            plt.bar(x, [value * 100 for value in strategy_return_list])

            plt.axhline(
                annualized_return_of_one_over_n * 100,
                linestyle=":",
                linewidth=2,
                label="1/N return"
            )

            tick_step = max(1, len(labels) // 30)

            plt.xticks(
                x[::tick_step],
                labels[::tick_step],
                rotation=90
            )

            plt.xlabel("Rebalancing frequency and safe distance")
            plt.ylabel("Annualized return (%)")
            plt.title("Rebalancing strategy returns with 1/N reference line")
            plt.legend()
            plt.tight_layout()
            plt.show()

            plt.figure(figsize=(14, 6))
            plt.bar(x, [value * 100 for value in no_rebalance_difference_list])
            plt.axhline(0, linewidth=1)
            tick_step = max(1, len(labels) // 30)

            plt.xticks(
                x[::tick_step],
                labels[::tick_step],
                rotation=90
            )

            plt.xlabel("Rebalancing frequency and safe distance")
            plt.ylabel("Difference in annualized return (% points)")
            plt.title("Rebalancing strategy minus no-rebalance strategy")
            plt.tight_layout()
            plt.show()

            max_value = max(return_list)
            max_index = return_list.index(max_value)

            best_parameters = parameter_list[max_index]

            print()
            print(f"Max return: {max_value*100:.2f}%")
            print(f"Rebalancing frequency: {best_parameters[0]} days, Safe distance: {best_parameters[1]*100:.0f}%")

        if choice == 6:
            simulate_one_over_n()
            
        if choice == 7:
            break
        

if __name__ == "__main__":
    main()
