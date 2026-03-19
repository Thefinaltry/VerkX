
def fetch_from_user(slice_output: bool = False):
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
                            short_bound == None
                        else:    
                            short_bound = int(short_bound)
                            if short_bound <= 0:
                                short_bound = -1*short_bound
                        while True:
                            try:
                                long_bound = input("How large can LONG positions get (%)?: ")
                                if long_bound.lower() in ["inf", 'infinite', 'max', 'unbound']:
                                    long_bound == None
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
    
    if short_bound != None:
        short_bound = float(short_bound)/100
    if short_bound != None:
        long_bound = float(long_bound)/100

    return period, efficient_frontier_period, short_bound, long_bound

def menu():
    while True:
        print("\n------ Efficient frontier (Iceland) ------")
        print("1. Plot efficient frontier")
        print("2. Calculate minimum variance portfolio")
        print("3. Test minimum variance porftolio performance")
        print("4. Test rebalancing strategy")
        print("5. exit")

        choice = input("Choose an option (1-5): ")

        if choice in ["1", "2", "3", "4", "5"]:
            return int(choice)
        else:
            print("Invalid choice. Please select a number between 1 and 4.")