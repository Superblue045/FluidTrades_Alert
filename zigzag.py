import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# get top 200 list
def get_top_list(api_key, limit):
    
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

    parameters = {
        'start': '1',
        'limit': limit,
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

def identify_supply_demand_zones(df):
    demand_zone = df['Close'].idxmin(), df['Close'].min()
    supply_zone = df['Close'].idxmax(), df['Close'].max()
    return demand_zone, supply_zone

def zigzag(s, c=0.05):   
    zz = []
    signal = 0
    inflection = s[0]
    
    for i in range(1, len(s)):
        # Find first trend
        if signal == 0:
            if s[i] <= (inflection - c):
                signal = -1
            if s[i] >= (inflection + c):
                signal = 1

        # Downtrend, inflection keeps track of the lowest point in the downtrend
        if signal == -1:
            # New Minimum, change inflection
            if s[i] < inflection:
                inflection = s[i]
            # Trend Reversal
            if s[i] >= (inflection + c):
                signal = 1
                zz.append(inflection)  # Append the lowest point of the downtrend to zz
                inflection = s[i]      # Current point becomes the highest point of the new uptrend
                continue

        # Uptrend, inflection keeps track of the highest point in the uptrend
        if signal == 1:
            # New Maximum, change inflection
            if s[i] > inflection:
                inflection = s[i]
            # Trend Reversal
            if s[i] <= (inflection - c):
                signal = -1
                zz.append(inflection)  # Append the highest point of the uptrend to zz
                inflection = s[i]      # Current point becomes the lowest point of the new trend
                continue
    return zz

if __name__ == "__main__": 
    api_key = '37b4a617-9609-48c6-8a41-d48db5b2ed44'
    limit = 50
    timeframe = '15'
    
    try:
        cryptocurrencies = get_top_list(api_key, limit)
        symbol_list = []
        
        for crypto in cryptocurrencies:
            symbol = crypto['symbol']
            symbol_list.append(symbol)
            
        zigzag_list = []
        supply_list = []
        demand_list = []
        
        for symbol in symbol_list:
            ohlc_data_list = get_ohlc_data(symbol, timeframe)
            if ohlc_data_list:
                date_list = [data_point[0] for data_point in ohlc_data_list]
                high_price_list = [data_point[1] for data_point in ohlc_data_list]
                low_price_list = [data_point[2] for data_point in ohlc_data_list]
                close_price_list = [data_point[3] for data_point in ohlc_data_list]
            
                data = {'Date': date_list, 'Close': close_price_list}
                current_price = close_price_list[-1]
                
                #------------- Zigzag ---------------
                s1 = data['Close']
                # Generate ZigZag points for each corresponding date
                points = zigzag(s1, c=0.0001)
                
                if len(points) > 0:
                    # print(f"ZigZag Points: {points}")
                    supply_point = points[0]
                    demand_point = points[0]
                    
                    for point in points:
                        if point > supply_point:
                            supply_point = point
                            
                    for point in points:
                        if point < demand_point:
                            demand_point = point
                    
                    # print(f"{symbol}: supply_point: {supply_point}")
                    # print(f"{symbol}: demand_point: {demand_point}")
                    
                    # print(f"{symbol}: current_price: {current_price}")
                    
                    if current_price <= demand_point:
                        print(f"The {symbol} is in the demand zone")
                        zigzag_list.append(symbol)
                    elif supply_point <= current_price:
                        print(f"The {symbol} is in the supply zone")
                        zigzag_list.append(symbol)
                #     else :
                #         print(f"{symbol} is not in demand or supply zone")
                # else:
                #     print(f"No ZigZag points found for {symbol}")
                
                # -------- supply and demand zone
                df = pd.DataFrame(data)
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                
                demand_zone, supply_zone = identify_supply_demand_zones(df)
                if current_price <= demand_zone[1]:
                    print(f"{symbol}: demand zone")
                    demand_list.append(symbol)
                elif current_price >= supply_zone[1]:
                    print(f"{symbol}: supply zone")
                    supply_list.append(symbol)

                # # Create a plot of the closing prices
                # plt.figure(figsize=(10, 6))
                # plt.plot(date_list, close_price_list, label='Close Price', color='blue')
                
                # # Plot ZigZag points for each corresponding date
                # plt.scatter(date_list[:len(points)], points, color='red', marker='o', label='ZigZag Points')
                # plt.axhline(y=demand_point, color='green', linestyle='--', label='Demand Zone')
                # plt.axhline(y=supply_point, color='red', linestyle='--', label='Supply Zone')
                
                # plt.xlabel('Date')
                # plt.ylabel('Price')
                # plt.title(f'{symbol} Closing Prices with ZigZag Points')
                # plt.xticks(rotation=45)
                # plt.legend()
                # plt.grid(True)
                # plt.tight_layout()
                
                # # Display the plot
                # plt.show()
                
        supply_compare_list = [item for item in zigzag_list if item in supply_list]
        demand_compare_list = [item for item in zigzag_list if item in demand_list]
        
        print(f"supply_compare_list: {supply_compare_list}")
        print(f"demand_compare_list: {demand_compare_list}")
                
    except Exception as e:
        print(str(e))