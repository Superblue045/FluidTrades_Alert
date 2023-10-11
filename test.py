import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime


def get_ohlc_data(symbol, timeframe):
    base_url = f'https://www.mexc.com/open/api/v2/market/kline?symbol={symbol}_USDT&interval={timeframe}m&limit=20'
    
    response = requests.get(base_url)
    all_data = response.json()
    
    ohlc_data_list = []
    
    if response.status_code == 200 and all_data['code'] == 200:
        for i in range(len(all_data['data'])):
            timestamp = all_data['data'][i][0]
            timestamp_datetime = datetime.utcfromtimestamp(timestamp)
            formatted_date = timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S')
            close_price = float(all_data['data'][i][2])
            high_price = float(all_data['data'][i][3])
            low_price = float(all_data['data'][i][4])
            
            ohlc_data_list.append((formatted_date, high_price, low_price, close_price))
    else:
        print(f"API request failed with status code: {response.status_code}")
        return None
    
    return ohlc_data_list

if __name__ == '__main__':
    
    symbol = 'XEC'
    timeframe = '15'
    time_ohlc_list = get_ohlc_data(symbol, timeframe)
    
    date_list = []
    high_price_list = []
    low_price_list = []
    
    if time_ohlc_list:
        for time_ohlc in time_ohlc_list:
            Date = time_ohlc[0]
            high_price = time_ohlc[1]
            low_price = time_ohlc[2]
            date_list.append(Date)
            high_price_list.append(high_price)
            low_price_list.append(low_price)

    data = {
        'Date': date_list,
        'High': high_price_list,
        'Low': low_price_list
    }

    df = pd.DataFrame(data)

    # Parameters
    swing_length = 10
    history_to_keep = 20

    # Calculate Swing Highs and Lows
    df['SwingHigh'] = df['High'].rolling(window=swing_length).max()
    df['SwingLow'] = df['Low'].rolling(window=swing_length).min()

    # Detect Supply and Demand Zones
    df['SupplyZone'] = np.where(df['High'] == df['SwingHigh'], 1, 0)
    df['DemandZone'] = np.where(df['Low'] == df['SwingLow'], -1, 0)

    # Create a new DataFrame to keep only the last 'history_to_keep' rows
    df = df.tail(history_to_keep)

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['High'], label='High', color='blue')
    plt.plot(df['Date'], df['Low'], label='Low', color='red')
    plt.scatter(df[df['SupplyZone'] == 1]['Date'], df[df['SupplyZone'] == 1]['High'], marker='^', color='green', label='Supply Zone')
    plt.scatter(df[df['DemandZone'] == -1]['Date'], df[df['DemandZone'] == -1]['Low'], marker='v', color='orange', label='Demand Zone')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'{symbol} Supply and Demand Zones')
    plt.xticks(rotation=45)  # Rotate x-axis labels for readability
    plt.legend()
    plt.grid(True)
    plt.tight_layout()  # Ensure labels fit within the figure boundaries
    plt.show()
