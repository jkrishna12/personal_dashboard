import pandas as pd
import yfinance as yf
from datetime import date
from currency_converter import CurrencyConverter
import numpy as np

class crypto_instrument():
    def __init__(self, ticker, shares, date, usd_date_bought):
        crypto_info = yf.Ticker(ticker).info
        self.name = crypto_info['name']
        self.ticker = crypto_info['symbol']
        self.type = crypto_info['quoteType'].capitalize()
        self.shares = shares
        self.date = date
        self.crypto_usd_bought = usd_date_bought
        self.current_price_gbp = yf.Ticker(ticker).history(period = '1d', interval = '1m').reset_index().iloc[-1]['Close']

        return

def etoro_dict_init():
    
    dict = {
        'name':[],
        'shortName':[],
        'type':[],
        'quantity':[],
        'Date':[],
        'avg_price_usd':[],
        'currentPrice_GBP':[],        
    }
    
    return dict

def crypto_currency_converter(df):
    
    c = CurrencyConverter()

    for i, row in df.iterrows():
        year, month, day = row['Date'].split('-')
    
        df.loc[i,'averagePrice_GBP'] = c.convert(row['avg_price_usd'], 'USD', 'GBP', date = date(int(year), int(month), int(day)))
    
    
    return df

def etoro_variables_init():
    
    btc_ticker = 'BTC-GBP'
    btc_shares = 0.00680005489766
    btc_date_bought = '2021-05-25'
    btc_usd_date_bought = 51004.69
    
    btc_class = crypto_instrument(btc_ticker, btc_shares, btc_date_bought, btc_usd_date_bought)
        
    eth_ticker = 'ETH-GBP'
    eth_shares = 0.0594297312567
    eth_date_bought = '2021-08-11'
    eth_usd_date_bought = 2867.42
    
    eth_class = crypto_instrument(eth_ticker, eth_shares, eth_date_bought, eth_usd_date_bought)   
    
    instrument_list = []
    instrument_list.extend([btc_class, eth_class])
    
    crypto_dict = etoro_dict_init()
    
    for instrument in instrument_list:
        crypto_dict['name'].append(instrument.name)
        crypto_dict['shortName'].append(instrument.ticker.split('-')[0])
        crypto_dict['type'].append(instrument.type)
        crypto_dict['quantity'].append(instrument.shares)
        crypto_dict['Date'].append(instrument.date)
        crypto_dict['avg_price_usd'].append(instrument.crypto_usd_bought)
        crypto_dict['currentPrice_GBP'].append(instrument.current_price_gbp)
    
    crypto_df = pd.DataFrame(crypto_dict)
    
    crypto_df = crypto_currency_converter(crypto_df)
    
    crypto_df['origPos'] = crypto_df['quantity'] * crypto_df['averagePrice_GBP']
    
    crypto_df['currentPos'] = crypto_df['quantity'] * crypto_df['currentPrice_GBP']
    
    crypto_df['abs_value_change'] = crypto_df.apply(lambda x: x['quantity'] * (x['currentPrice_GBP'] - x['averagePrice_GBP']), axis = 1)
    
    crypto_df['pct_change'] = crypto_df.apply(lambda x: ((x['currentPrice_GBP'] - x['averagePrice_GBP']) / x['averagePrice_GBP']) * 100, axis = 1)
    
    crypto_df['Date'] = pd.to_datetime(crypto_df['Date'], format = '%Y-%m-%d')
    
    columns_to_round = {
        'quantity':4,
        'avg_price_usd':2,
        'currentPrice_GBP':2,
        'averagePrice_GBP':2,
        'abs_value_change':2,
        'origPos':2,
        'currentPos':2,
        'pct_change':2
    }

    crypto_df = crypto_df.round(columns_to_round) 
    
    c = CurrencyConverter()

    etoro_cash = 37.9
    
    etoro_cash_gbp = np.round(c.convert(etoro_cash, 'USD', 'GBP'), 2)                                                                          
    
    return crypto_df, etoro_cash_gbp













