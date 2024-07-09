"""
(myenv) harish $ python binancePull.py BOMEUSDT 15m 2023-06-30
BOMEUSDT historical data saved to 'BOMEUSDT_15m_data.csv'
"""
import requests
import csv
import sys
from datetime import datetime, timedelta

# Get the coin name, interval, and start date from command-line arguments
if len(sys.argv) != 4:
    print("Usage: python script.py <coin_name> <interval> <start_date>")
    sys.exit(1)

coin_ticker = sys.argv[1]
interval = sys.argv[2]
start_date_str = sys.argv[3]

try:
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
except ValueError:
    print("Invalid date format. Please use 'YYYY-MM-DD'.")
    sys.exit(1)

end_date = datetime.now()

end_time = int(end_date.timestamp() * 1000) # convert to milliseconds
start_time = int(start_date.timestamp() * 1000)

url = "https://api.binance.com/api/v3/klines"
params = {
    "symbol": coin_ticker,
    "interval": interval,
    "limit": 1000,
    "startTime": start_time,
    "endTime": end_time
}

with open(f"{coin_ticker}_{interval}_data.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    writer.writerow(["Open Time", "Open", "High", "Low", "Close", "Volume"])

    while start_time <= end_time:
        response = requests.get(url, params=params)
        data = response.json()
        
        for candle in data:
            open_time = datetime.fromtimestamp(candle[0] / 1000).strftime('%Y-%m-%d')
            open_price = candle[1]
            high_price = candle[2]
            low_price = candle[3]
            close_price = candle[4]
            volume = candle[5]
            writer.writerow([open_time, open_price, high_price, low_price, close_price, volume])
        
        start_time = data[-1][0] + 86400000  # Add 1 day in milliseconds
        params["startTime"] = start_time

print(f"{coin_ticker} historical data saved to '{coin_ticker}_{interval}_data.csv'")
