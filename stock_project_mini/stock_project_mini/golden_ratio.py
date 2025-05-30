import warnings
warnings.simplefilter(action='ignore', category=Warning)
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objs as go
import plotly.express as px

# Define Golden Cross Signal for Signal Generation
def GoldenCrossverSignal(name, data_point):
    path = f'Data/{name}.csv'
    data = pd.read_csv(path, parse_dates=['Date'], index_col='Date')
    data['20_SMA'] = data.Close.rolling(window=20, min_periods=1).mean()
    data['50_SMA'] = data.Close.rolling(window=50, min_periods=1).mean()
    data['Signal'] = 0
    data['Signal'] = np.where(data['20_SMA'] > data['50_SMA'], 1, 0)
    data['Position'] = data.Signal.diff()
    
    df_pos = data.iloc[-data_point:][(data.iloc[-data_point:]['Position'] == 1) | (data['Position'] == -1)].copy()
    df_pos['Position'] = df_pos['Position'].apply(lambda x: 'Buy' if x == 1 else 'Sell')
    
    trace_close = go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price', line=dict(color='black'))
    trace_20sma = go.Scatter(x=data.index, y=data['20_SMA'], mode='lines', name='20-day SMA', line=dict(color='blue'))
    trace_50sma = go.Scatter(x=data.index, y=data['50_SMA'], mode='lines', name='50-day SMA', line=dict(color='green'))
    trace_buy = go.Scatter(x=data.iloc[-data_point:][data.iloc[-data_point:]['Position'] == 1].index, 
                           y=data.iloc[-data_point:]['20_SMA'][data.iloc[-data_point:]['Position'] == 1], 
                           mode='markers', name='Buy', marker=dict(symbol='triangle-up', size=15, color='green'))
    trace_sell = go.Scatter(x=data.iloc[-data_point:][data.iloc[-data_point:]['Position'] == -1].index, 
                            y=data.iloc[-data_point:]['20_SMA'][data.iloc[-data_point:]['Position'] == -1], 
                            mode='markers', name='Sell', marker=dict(symbol='triangle-down', size=15, color='red'))
    
    layout = go.Layout(
        title=name,
        xaxis=dict(title='Date'),
        yaxis=dict(title='Price in Rupees'),
        showlegend=True
    )
    
    fig = go.Figure(data=[trace_close, trace_20sma, trace_50sma, trace_buy, trace_sell], layout=layout)
    
    return fig, df_pos

# Define Golden Cross Signal for Backtesting
def GoldenCrossverSignalBacktest(name):
    path = f'Data/{name}.csv'
    data = pd.read_csv(path, parse_dates=['Date'], index_col='Date')
    data['Prev_Close'] = data.Close.shift(1)
    data['20_SMA'] = data.Prev_Close.rolling(window=20, min_periods=1).mean()
    data['50_SMA'] = data.Prev_Close.rolling(window=50, min_periods=1).mean()
    data['Signal'] = 0
    data['Signal'] = np.where(data['20_SMA'] > data['50_SMA'], 1, 0)
    data['Position'] = data.Signal.diff()
    df_pos = data[(data['Position'] == 1) | (data['Position'] == -1)].copy()
    df_pos['Position'] = df_pos['Position'].apply(lambda x: 'Buy' if x == 1 else 'Sell')
    return df_pos

# Backtest class
class Backtest:
    def __init__(self):
        self.columns = ['Equity Name', 'Trade', 'Entry Time', 'Entry Price', 'Exit Time', 'Exit Price', 'Quantity', 'Position Size', 'PNL', '% PNL']
        self.backtesting = pd.DataFrame(columns=self.columns)

    def buy(self, equity_name, entry_time, entry_price, qty):
        self.trade_log = dict(zip(self.columns, [None] * len(self.columns)))
        self.trade_log['Trade'] = 'Long Open'
        self.trade_log['Quantity'] = qty
        self.trade_log['Position Size'] = round(self.trade_log['Quantity'] * entry_price, 3)
        self.trade_log['Equity Name'] = equity_name
        self.trade_log['Entry Time'] = entry_time
        self.trade_log['Entry Price'] = round(entry_price, 2)

    def sell(self, exit_time, exit_price, exit_type, charge):
        self.trade_log['Trade'] = 'Long Closed'
        self.trade_log['Exit Time'] = exit_time
        self.trade_log['Exit Price'] = round(exit_price, 2)
        self.trade_log['Exit Type'] = exit_type
        self.trade_log['PNL'] = round((self.trade_log['Exit Price'] - self.trade_log['Entry Price']) * self.trade_log['Quantity'] - charge, 3)
        self.trade_log['% PNL'] = round((self.trade_log['PNL'] / self.trade_log['Position Size']) * 100, 3)
        self.trade_log['Holding Period'] = str(exit_time - self.trade_log['Entry Time'])
        self.backtesting = self.backtesting.append(self.trade_log, ignore_index=True)

# Streamlit app layout
st.title("Golden Crossover Signal for Stocks")

stock_name = st.text_input("Enter the stock name:", "TATAMOTORS")
data_point = st.number_input("Enter the number of data points for signal generation:", min_value=1, value=300)
capital = st.number_input("Enter the initial capital for backtesting:", min_value=1, value=50000)

if st.button("Generate Signal"):
    fig, df_pos = GoldenCrossverSignal(stock_name, data_point)
    st.plotly_chart(fig)

    st.subheader("Buy/Sell Signals")
    st.dataframe(df_pos[['Close', 'Position']].reset_index())
