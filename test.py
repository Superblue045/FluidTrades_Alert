import requests
import ccxt
import pandas as pd
# import dontshareconfig
import time
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
import numpy as np
# import nice_funcs as n

phemex = ccxt.phemex({
  'enableRateLimit': True,
  'apiKey': dontshareconfig.xp_j_KEY,
  'secret': dontshareconfig.xp_j_SECRET,
})

symbol = 'ETHUSD'
size = 1000

def supply_demand_zones(symbol=symbol):
  
  '''
  out puts a dg with supply and demand zones for each time frame
  #this is supply zone and demand zone ranges
  $row 0 is the CLOSE, row 1 is the WICK (high/low)
  # and the supply/demand zone is inbetween the two
  '''
  
  print('starting supply and demand zone calculations..')
  
  #get OHLCV data
  sd_limit = 200
  sd_sma = 20
  
  df_1m = n.df_sma(symbol, '1m', sd_limit, sd_sma)
  
  print(df_1m)
  
  sd_df = pd.DataFrame() #Supply and demand zone dataframe
  
  #get support and resistance
  supp_1m = df_1m.iloc[-1]['support']
  resis_1m = df_1m.iloc[-1]['resis']
  
  df_1m['supp_lo'] = df_1m[:2]['low'].min
  supp_lo_1m = df_1m.iloc[-1]['supp_lo']  
  
  df_1m['res_hi'] = df_1m[:2]['high'].max
  res_hi_1m = df_1m.iloc[-1]['res_hi']
  
  sd_df['1m_dz'] = [supp_lo_1m, supp_1m]
  sd_df['1m_sz'] = [res_hi_1m, resis_1m]
  
  time.sleep(1)
  
  df_5m = n.df_sma(symbol, '5m', sd_limit, sd_sma)
  supp_5m = df_5m.iloc[-1]['support']
  resis_5m = df_5m.iloc[-1]['resis']
  
  df_5m['supp_lo'] = df_5m[:2]['low'].min()
  supp_lo_5m = df_5m.iloc[-1]['supp_lo']
  
  df_5m['res_hi'] = df_5m[:2]['high'].max()
  res_hi_5m = df_5m.iloc[-1]['res_hi']
  
  sd_df['5m_dz'] = [supp_lo_5m, supp_5m]
  sd_df['5m_sz'] = [res_hi_5m, resis_5m]
  
  time.sleep(1)
  
  df_15m = n.df_sma(symbol, '15m', sd_limit, sd_sma)
  
  supp_15m = df_15m.iloc[-1]['support']
  resis_15m = df_15m.iloc[-1]['resis']
  
  df_15m['supp_lo'] = df_15m[:-2]['low'].min()
  supp_lo_15m = df_15m.iloc[-1]['supp_lo']
  
  df_15m['res_hi'] = df_15m[:-2]['high'].max()
  res_hi_15m = df_15m.iloc[-1]['res_hi']
  
  sd_df['15m_dz'] = [supp_lo_15m, supp_15m]
  sd_df['15m_sz'] = [res_hi_15m, resis_15m]
  
  time.sleep(1)
  
  df_1h = n.df_sma(symbol, '1h', sd_limit, sd_sma)
  
  supp_1h = df_1h.iloc[-1]['support']
  resis_1h = df_1h.iloc[-1]['resis']

  df_1h['supp_lo'] = df_1h[:-2]['low'].min()
  supp_lo_1h = df_1h.iloc[-1]['res_hi'] 
  
  df_1h['res_hi'] = df_1h[:-2]['high'].max()
  res_hi_1h = df_1h.iloc[-1]['res_hi']
  
  sd_df['1h_dz'] = [supp_lo_1h, supp_1h]
  sd_df['1h_sz'] = [res_hi_1h, resis_1h]
  
  time.sleep(1)
  
  df_4h = n.df_sma(symbol, '4h', sd_limit, sd_sma)
  
  supp_4h = df_4h.iloc[-1]['support']
  resis_4h = df_4h.iloc[-1]['resis']

  df_4h['supp_lo'] = df_1h[:-2]['low'].min()
  supp_lo_4h = df_1h.iloc[-1]['res_hi'] 
  
  df_4h['res_hi'] = df_1h[:-2]['high'].max()
  res_hi_4h = df_1h.iloc[-1]['res_hi']
  
  sd_df['4h_dz'] = [supp_lo_4h, supp_4h]
  sd_df['4h_sz'] = [res_hi_4h, resis_4h]
  
  time.sleep(1)
  
  df_1d = n.df_sma(symbol, '1d', sd_limit, sd_sma)
  
  supp_1d = df_1d.iloc[-1]['support']
  resis_1d = df_1d.iloc[-1]['resis']

  df_1d['supp_lo'] = df_1d[:-2]['low'].min()
  supp_lo_1d = df_1h.iloc[-1]['res_hi'] 
  
  df_1d['res_hi'] = df_1d[:-2]['high'].max()
  res_hi_1d = df_1d.iloc[-1]['res_hi']
  
  sd_df['1d_dz'] = [supp_lo_1d, supp_1d]
  sd_df['1d_sz'] = [res_hi_1d, resis_1d]
  
  
def sz_bot():
  sd_df = supply_demand_zones(symbol)
  print(sd_df)
    