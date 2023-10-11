import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Function to get OHLC data
def get_ohlc_data(symbol, timeframe):
    base_url = f'https://www.mexc.com/open/api/v2/market/kline?symbol={symbol}_USDT&interval={timeframe}m&limit=60'
    response = requests.get(base_url)
    all_data = response.json()
    
    ohlc_data_list = []
    
    if response.status_code == 200 and all_data['code'] == 200:
        for data_point in all_data['data']:
            timestamp = data_point[0]
            timestamp_datetime = datetime.utcfromtimestamp(timestamp)
            formatted_date = timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S')
            close_price = float(data_point[2])
            high_price = float(data_point[3])
            low_price = float(data_point[4])
            
            ohlc_data_list.append((formatted_date, high_price, low_price, close_price))
    else:
        print(f"API request failed with status code: {response.status_code}")
        return None
    
    return ohlc_data_list

# Function to identify supply and demand zones
def identify_supply_demand_zones(df):
    demand_zone = df['Close'].idxmin(), df['Close'].min()
    supply_zone = df['Close'].idxmax(), df['Close'].max()
    return demand_zone, supply_zone

# Function to plot price chart with zones
def plot_price_chart(df, symbol, demand_zone, supply_zone):
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['Close'], label='Price', color='blue')
    
    plt.axhline(y=demand_zone[1], color='green', linestyle='--', label='Demand Zone')
    plt.axhline(y=supply_zone[1], color='red', linestyle='--', label='Supply Zone')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'{symbol} Supply and Demand Zones')
    plt.legend()
    plt.grid()
    plt.show()

# Main function
if __name__ == '__main__':
    api_key = '37b4a617-9609-48c6-8a41-d48db5b2ed44'
    symbols = ['BTC']
    timeframe = '15'
    
    for symbol in symbols:
        try:
            ohlc_data_list = get_ohlc_data(symbol, timeframe)
            if ohlc_data_list:
                date_list = [data_point[0] for data_point in ohlc_data_list]
                high_price_list = [data_point[1] for data_point in ohlc_data_list]
                low_price_list = [data_point[2] for data_point in ohlc_data_list]
                close_price_list = [data_point[3] for data_point in ohlc_data_list]
                
                data = {'Date': date_list, 'Close': close_price_list}
                df = pd.DataFrame(data)
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                
                demand_zone, supply_zone = identify_supply_demand_zones(df)
                current_price = close_price_list[-1]
                
                print(f"Symbol: {symbol}")
                print(f"Demand Zone: {demand_zone}")
                print(f"Supply Zone: {supply_zone}")
                print(f"Current Price: {current_price}")
                
                plot_price_chart(df, symbol, demand_zone, supply_zone)
                
            else:
                print(f"No OHLC data available for {symbol}.")
             
        except Exception as e:
            print(str(e))
