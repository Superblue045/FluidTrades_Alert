import requests
import pandas as pd
import requests
from datetime import datetime
import matplotlib.pyplot as plt

# get top 200 list
def get_top_list(api_key):
    
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

    parameters = {
        'start': '1',
        'limit': '1',
        'sort': 'market_cap',
        'convert': 'USD',
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }

    response = requests.get(url, headers=headers, params=parameters)

    data = response.json()

    if response.status_code == 200 and data['status']['error_code'] == 0:
        return data['data']
    else:
        error_message = data['status']['error_message']
        raise Exception(f"API request failed. Error: {error_message}")

# get OHLC data using MEXC api
def get_ohlc_data(symbol, timeframe):
    base_url = f'https://www.mexc.com/open/api/v2/market/kline?symbol={symbol}_USDT&interval={timeframe}m&limit=100'
    
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
    
    api_key = '37b4a617-9609-48c6-8a41-d48db5b2ed44'
    
    try:
        top_list = get_top_list(api_key)
        
        print(f"top_list: {top_list}")
        
        for currency in top_list:
            
            # symbol = currency['symbol']
            symbol = 'ETH'
            timeframe = '15'
            time_ohlc_list = get_ohlc_data(symbol, timeframe)
                    
            date_list = []
            close_price_list = []
            
            if time_ohlc_list:
                for time_ohlc in time_ohlc_list:
                    Date = time_ohlc[0]
                    close_price = time_ohlc[3]
                    date_list.append(Date)
                    close_price_list.append(close_price)
                
                print(f"close_price_list: {close_price_list}")
                    
                # historical price data
                data = {'Date': date_list,
                        'Close': close_price_list}
                df = pd.DataFrame(data)
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                
                # Plot the price chart
                plt.figure(figsize=(10, 5))
                plt.plot(df.index, df['Close'], label='Price', color='blue')

                # Identify potential supply and demand zones
                demand_zone = df['Close'].idxmin(), df['Close'].min()
                supply_zone = df['Close'].idxmax(), df['Close'].max()
                
                current_price = close_price_list[-1]
                demand_price = demand_zone[1]
                supply_price = supply_zone[1]
                
                print(f"current_price: {current_price}, demand_price: {demand_price}, supply_price: {supply_price}")
                
                if current_price >= supply_price:
                    print(f"current_price: {current_price}, supply_price: {supply_price}")
                
                if current_price <= demand_price:
                    print(f"current_price: {current_price}, supply_price: {demand_price}")
                    
                    # Plot supply and demand zones
                plt.axhline(y=demand_zone[1], color='green', linestyle='--', label='Demand Zone')
                plt.axhline(y=supply_zone[1], color='red', linestyle='--', label='Supply Zone')

                # Add labels and legend
                plt.xlabel('Date')
                plt.ylabel('Price')
                plt.title(f'{symbol} Supply and Demand Zones')
                plt.legend()

                # Show the plot
                plt.grid()
                plt.show()
                
            else:
                print("No OHLC data available for this symbol.")
             
    except Exception as e:
        print(str(e))
