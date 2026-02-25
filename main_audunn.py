from get_data import get_data, cagr_over_available, years_available

prices = get_data(country="iceland", period="5y", interval="1d")

cagr = cagr_over_available(prices, periods_per_year=252, min_periods=120)
yrs = years_available(prices, periods_per_year=252)

print("CAGR:")
print(cagr)

print("\nYears used (approx):")
print(yrs[cagr.index].round(2))

s = prices["REITIR.IC"].dropna()

print("Start date:", s.index[0])
print("End date:", s.index[-1])
print("Start price:", s.iloc[0])
print("End price:", s.iloc[-1])
print("Years used:", (len(s)-1)/252)
print("Raw ratio:", s.iloc[-1] / s.iloc[0])


#Hér er til dæmis Arion end price 201 og beginning price, 88.583, þegar við margföldum 88*(1+0.180392)^4.94, þá fáum við = 201 og stemmir þá að annual average return hjá Arion banka er 18%,  alvöru price a arion 25.feb 21' var btw 118.5 en ekki 88.58 það er nuþegar dividend adjusted sem er gott fyrir okkur