import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt

class CoinMarketCapDataPull:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical'
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }

    def fetch_data(self, symbol, start_date, end_date, interval='daily'):
        parameters = {
            'symbol': symbol,
            'time_start': start_date,
            'time_end': end_date,
            'interval': interval
        }
        response = requests.get(self.base_url, headers=self.headers, params=parameters)
        print(self.base_url,self.headers,parameters)
        data = response.json()
        return data

    def get_data(self, symbol, time_interval, last_period):
        end_date = pd.Timestamp.today()
        if time_interval == 'months':
            start_date = end_date - pd.DateOffset(months=last_period)
        elif time_interval == 'days':
            start_date = end_date - pd.DateOffset(days=last_period)
        elif time_interval == 'hours':
            start_date = end_date - pd.DateOffset(hours=last_period)
        elif time_interval == 'minutes':
            start_date = end_date - pd.DateOffset(minutes=last_period)
        else:
            raise ValueError("Invalid time interval. Choose from 'months', 'days', 'hours', 'minutes'.")
        
        data = self.fetch_data(symbol, start_date.strftime('%Y-%m-%dT%H:%M:%SZ'), end_date.strftime('%Y-%m-%dT%H:%M:%SZ'), interval=time_interval)
        print(data)
        df = self.process_data(data)
        self.store_data(df, symbol, time_interval, last_period)
        return df

    def process_data(self, data):
        ohlcv = data['data']['quotes']
        df = pd.DataFrame(ohlcv)
        df['timestamp'] = pd.to_datetime(df['time_open'])
        df.set_index('timestamp', inplace=True)
        df = df[['quote']].apply(lambda x: pd.Series(x[0]))
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Market Cap']
        return df

    def store_data(self, df, symbol, time_interval, last_period):
        filename = f'{symbol}_{time_interval}_{last_period}.csv'
        filepath = os.path.join(self.storage_path, filename)
        df.to_csv(filepath)

    def get_last_6_months_data(self, symbol):
        return self.get_data(symbol, 'months', 6)

    def get_last_4_years_data(self, symbol):
        return self.get_data(symbol, 'months', 48)

# Usage example
api_key = ''
cmc = CoinMarketCapDataPull(api_key)

# Fetch the last 6 months of Bitcoin data
df_6_months = cmc.get_last_6_months_data('BTC')
#print(df_6_months.head())

# Fetch the last 4 years of Bitcoin data
#df_4_years = cmc.get_last_4_years_data('BTC')
#print(df_4_years.head())

