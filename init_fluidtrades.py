import requests
import numpy as np
from datetime import datetime
import threading
import time
import matplotlib.pyplot as plt
    
# get OHLC data using MEXC api
def get_ohlc_data(symbol, timeframe):
   
    base_url = f'https://www.mexc.com/open/api/v2/market/kline?symbol={symbol}_USDT&interval={timeframe}m&limit=200'

    response = requests.get(base_url)
    all_data = response.json()

    ohlc_data_list = []

    if all_data['code'] == 200:
        for i in range(len(all_data['data'])):
            timestamp = all_data['data'][i][0]
            timestamp_datetime = datetime.utcfromtimestamp(timestamp)
            formatted_date = timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S')
            close_price = float(all_data['data'][i][2])
            high_price = float(all_data['data'][i][3])
            low_price = float(all_data['data'][i][4])
            
            ohlc_data_list.append((formatted_date, high_price, low_price, close_price))

        return ohlc_data_list

# Function to calculate ATR (Average True Range)
def calculate_atr(high_prices, low_prices, close_prices, period):
    true_ranges = []
    for i in range(1, len(high_prices)):
        true_range = max(high_prices[i] - low_prices[i], abs(high_prices[i] - close_prices[i - 1]), abs(low_prices[i] - close_prices[i - 1]))
        true_ranges.append(true_range)    
    atr_values = [np.nan] * (period - 1)
    
    for i in range(period - 1, len(true_ranges)):
        atr_value = np.mean(true_ranges[i - period + 1 : i + 1])
        atr_values.append(atr_value)
    
    return np.array(atr_values)

# Function to detect swing highs
def detect_swing_highs(high_prices, length):
    return np.array([np.nan] * (length - 1) + [np.nanmax(high_prices[i - length + 1 : i + 1]) for i in range(length - 1, len(high_prices))])

# Function to detect swing lows
def detect_swing_lows(low_prices, length):
    return np.array([np.nan] * (length - 1) + [np.nanmin(low_prices[i - length + 1 : i + 1]) for i in range(length - 1, len(low_prices))])

# Function to check for overlap with existing zones
def check_overlap(new_poi, zones, atr):
    atr_threshold = atr * 2
    for zone in zones:
        top, bottom = zone[1], zone[2]
        poi = (top + bottom) / 2
        upper_boundary = poi + atr_threshold
        lower_boundary = poi - atr_threshold
        if lower_boundary <= new_poi <= upper_boundary:
            return True
    return False

# Function to detect supply and demand zones
def detect_supply_demand_zones(time_ohlc_data):
    formatted_date = np.array([entry[0] for entry in time_ohlc_data])
    high_prices = np.array([entry[1] for entry in time_ohlc_data])
    low_prices = np.array([entry[2] for entry in time_ohlc_data])
    close_prices = np.array([entry[3] for entry in time_ohlc_data])

    atr_period = 10
    atr = calculate_atr(high_prices, low_prices, close_prices, atr_period)
    
    swing_length = 10
    swing_highs = detect_swing_highs(high_prices, swing_length)
    swing_lows = detect_swing_lows(low_prices, swing_length)

    supply_zones = []
    demand_zones = []

    for i in range(len(swing_highs)):
        if i >= swing_length:
            if close_prices[i] >= swing_highs[i]:
                atr_buffer = atr[i] * 2
                supply_zone_top = swing_highs[i]
                supply_zone_bottom = supply_zone_top - atr_buffer
                poi = (supply_zone_top + supply_zone_bottom) / 2

                if not check_overlap(poi, supply_zones, atr):
                    supply_zones.append((formatted_date[i], supply_zone_top, supply_zone_bottom))

    for i in range(len(swing_lows)):
        if i >= swing_length:
            if close_prices[i] <= swing_lows[i]:
                atr_buffer = atr[i] * 2
                demand_zone_bottom = swing_lows[i]
                demand_zone_top = demand_zone_bottom + atr_buffer
                poi = (demand_zone_top + demand_zone_bottom) / 2

                if not check_overlap(poi, demand_zones, atr):
                    demand_zones.append((formatted_date[i], demand_zone_top, demand_zone_bottom))
                    
    return supply_zones, demand_zones

if __name__ == '__main__':

    # Fetch OHLCV data for a specific trading pair and timeframe
    symbol = 'ETH'
    timeframe = '15'
    time_ohlc_data = get_ohlc_data(symbol, timeframe)

    # Detect supply and demand zones
    supply_zones, demand_zones = detect_supply_demand_zones(time_ohlc_data)
    
    print(f"supply_zones: {supply_zones}")
    print(f"demand_zones: {demand_zones}")
    
    # Extract data for plotting
    formatted_date = [entry[0] for entry in time_ohlc_data]
    high_prices = [entry[1] for entry in time_ohlc_data]
    low_prices = [entry[2] for entry in time_ohlc_data]
    close_prices = [entry[3] for entry in time_ohlc_data]

    # Create a plot for OHLC data
    plt.figure(figsize=(12, 6))
    plt.plot(formatted_date, high_prices, label='High')
    plt.plot(formatted_date, low_prices, label='Low')
    plt.plot(formatted_date, close_prices, label='Close', linestyle='--', alpha=0.7)
    
    # Plot supply zones
    if supply_zones:
        supply_dates = [entry[0] for entry in supply_zones]
        supply_tops = [entry[1] for entry in supply_zones]
        supply_bottoms = [entry[2] for entry in supply_zones]
        plt.scatter(supply_dates, supply_tops, color='red', marker='^', label='Supply Zone Tops')
        plt.scatter(supply_dates, supply_bottoms, color='green', marker='v', label='Supply Zone Bottoms')
    
    # Plot demand zones
    if demand_zones:
        demand_dates = [entry[0] for entry in demand_zones]
        demand_tops = [entry[1] for entry in demand_zones]
        demand_bottoms = [entry[2] for entry in demand_zones]
        plt.scatter(demand_dates, demand_tops, color='blue', marker='^', label='Demand Zone Tops')
        plt.scatter(demand_dates, demand_bottoms, color='orange', marker='v', label='Demand Zone Bottoms')

    # Set plot labels and legend
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'OHLC and Supply/Demand Zones for {symbol} ({timeframe}-minute timeframe)')
    plt.legend()
    
    # Show the plot
    plt.grid(True)
    plt.show()
        
    