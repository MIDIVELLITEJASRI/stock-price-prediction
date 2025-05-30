import yfinance as yf
import pandas as pd

equity_details = pd.read_csv('EQUITY_L.csv') # All Details for NSE stocks : Symbol is the required field
for name in equity_details.SYMBOL:
    try:
        data = yf.download(f'{name}.NS')
        data.to_csv(f'./Data/{name}.csv') # Data will be stored in data folder
    except Exception as e:
        print(f'{name} ===> {e}')
