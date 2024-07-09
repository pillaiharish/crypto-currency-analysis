import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt
import os

class CryptoDataPull:
    def __init__(self, storage_path='data'):
        self.storage_path = storage_path
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

    def fetch_data(self, symbol, start_date, end_date, interval='1d'):
        df = yf.download(symbol, start=start_date, end=end_date, interval=interval)
        return df

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
        
        interval = '15m' if time_interval == 'minutes' else '1d'
        df = self.fetch_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), interval=interval)
        self.store_data(df, symbol, time_interval, last_period)
        return df

    def store_data(self, df, symbol, time_interval, last_period):
        filename = f'{symbol}_{time_interval}_{last_period}.csv'
        filepath = os.path.join(self.storage_path, filename)
        df.to_csv(filepath)

    def load_data(self, symbol, time_interval, last_period):
        filename = f'{symbol}_{time_interval}_{last_period}.csv'
        filepath = os.path.join(self.storage_path, filename)
        return pd.read_csv(filepath, index_col='Datetime', parse_dates=True)

    def clean_data(self, df):
        df = df.dropna()  # Drop rows with missing values
        return df

    def prepare_data_for_lstm(self, df, time_step=60):
        # Normalize the data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(df[['Open', 'High', 'Low', 'Close', 'Volume']])

        # Create sequences
        def create_dataset(dataset, time_step=1):
            X, Y = [], []
            for i in range(len(dataset) - time_step - 1):
                a = dataset[i:(i + time_step), :]
                X.append(a)
                Y.append(dataset[i + time_step, 3])  # Use 'Close' price as the target
            return np.array(X), np.array(Y)

        X, y = create_dataset(scaled_data, time_step)
        X = X.reshape(X.shape[0], X.shape[1], X.shape[2])
        return X, y, scaler

# Usage example
crypto = CryptoDataPull()

# Fetch and store the last 6 months of 15-minute interval Bitcoin data
df_15m_6months = crypto.get_data('BTC-USD', 'minutes', 6*30*24*4)  # 6 months

# Load the stored data
#df_15m_6months_loaded = crypto.load_data('BTC-USD', 'minutes', 6*30*24*4)

# Clean the data
#df_15m_6months_cleaned = crypto.clean_data(df_15m_6months_loaded)

# Prepare the data for LSTM
#X, y, scaler = crypto.prepare_data_for_lstm(df_15m_6months_cleaned)

#print(X.shape, y.shape)

