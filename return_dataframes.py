import pandas as pd
import api_connection as api 
from currency_converter import CurrencyConverter
import time
import re


def get_portfolio_df(api_key):
    """
    Function takes in an api key and returns a Pandas Dataframe of the
    portfolio data
    """  
    # extract json portfolio data using api key
    data = api.get_portfolio(api_key)
    
    # create a dataframe using the json data
    portfolio_df = pd.json_normalize(data)[['ticker','quantity','averagePrice', 'currentPrice', 'ppl', 'fxPpl', 'initialFillDate']]
    
    return portfolio_df
    

def get_instrument_df(api_key):
    """
    Function takes in an api key and returns a Pandas Dataframe of the
    instrument data
    """  
    # extract json instrument data using api key   
    data_instrument = api.get_instrument_data(api_key)
    
    # create a dataframe using the json data    
    instrument_df = pd.json_normalize(data_instrument)[['ticker', 'type', 'currencyCode', 'name', 'shortName']]
    
    return instrument_df

def get_instrument_portfolio_merge_df(api_key):
    """
    Function takes in the api key and returns a merged Pandas dataframe
    selecting the relevant columns of the instrument and portfolio dataframe
    """
    # find the portfolio dataframe using get_portfolio_df function
    portfolio_df = get_portfolio_df(api_key)
    
    col_name = portfolio_df.columns[0]
    time.sleep(10)
    
    # find the instrument dataframe using the get_instrument_df function
    instrument_df = get_instrument_df(api_key)
    time.sleep(10)
    
    instrument_col_name = instrument_df.columns[0]
    
    rename_dict = {instrument_col_name:col_name}
    
    instrument_df_rename = instrument_df.rename(columns = rename_dict)
       
    # merges the portfolio dataframe and the instrument dataframe on the ticker column
    portfolio_df_merge = portfolio_df.merge(instrument_df_rename, on = 'ticker')    
       
    return portfolio_df_merge

def currency_converter(df):
    """
    Function takes in a dataframe and returns the same dataframe with an 
    additional 2 columns: the average price in GBP and the
    currentPrice in GBP
    """
    
    # create a currency converter object
    c = CurrencyConverter()
    
    # loop through rows of dataframe   
    for i, row in df.iterrows():
        
        # calculate the average price in GBP of the stock on the day it was bought
        df.loc[i, 'averagePrice_GBP'] = c.convert(row['averagePrice'], row['currencyCode'], 'GBP', row['date_bought'])
        
        # calculates the current price in GBP of the stock on the current day
        df.loc[i, 'currentPrice_GBP'] = c.convert(row['currentPrice'], row['currencyCode'], 'GBP')
    
    return df

def get_clean_portfolio_df(api_key):
    """
    Function takes in the api key and returns a clean Pandas Dataframe. 
    Renames columns, calculates relevant features and corrects the GBX issue
    """
    
    # merged dataframe of the instrument and portfolio dataframes
    portfolio_df = get_instrument_portfolio_merge_df(api_key)
    
    # dictionary of the columns to rename
    rename_dict = {'ppl':'abs_value_change', 'fxPpl':'fx_value_change',
                   'initialFillDate':'date_bought'}
    
    # renames the columns of the portfolio dataframe
    portfolio_df.rename(columns = rename_dict, inplace = True)
    
    # convertes the date_bought column to datetime format
    portfolio_df['date_bought'] = pd.to_datetime(portfolio_df['date_bought'], utc = True)
    
    # multiplies the GBX averagePrice, currentPrice columns by 0.01
    # converts these values from pennies to pounds
    portfolio_df.loc[portfolio_df['currencyCode'] == 'GBX', ['averagePrice', 'currentPrice']] = portfolio_df.loc[portfolio_df['currencyCode'] == 'GBX', ['averagePrice', 'currentPrice']] * 0.01
    
    # renames the GBX column to GBP 
    portfolio_df.loc[portfolio_df['currencyCode'] == 'GBX','currencyCode'] = 'GBP'
    
    # convert the averagePrice and currentPrice into GBP
    portfolio_df = currency_converter(portfolio_df)
    
    # find the current value of all open positions
    portfolio_df['currentPos'] = portfolio_df['quantity'] * portfolio_df['currentPrice_GBP']
    
    # calculate the percentage change of the stocks
    portfolio_df['pct_change'] = portfolio_df.apply(lambda x: (x['abs_value_change'] / (x['quantity'] * x['averagePrice_GBP']) * 100), axis = 1)
    
    # round the dataframe to 2dp
    portfolio_df = portfolio_df.round(decimals = 2)
    
    return portfolio_df

def get_dividends_df(api_key):
    """
    Function takes in api key and returns a cleaned pandas dataframe of dividends
    """
    # get dividend data
    dividends = api.get_dividends(api_key)
    
    # convert list of dicts into a pandas dataframe
    dividends_df = pd.json_normalize(dividends)
    
    # convert paidOn to datetime dtype and ticker column to string dtype
    dividends_df['paidOn'] = pd.to_datetime(dividends_df['paidOn'], utc = True).dt.date
    dividends_df['paidOn'] = pd.to_datetime(dividends_df['paidOn'], format = '%Y-%m-%d')
    dividends_df['ticker'] = dividends_df['ticker'].astype('string')

    # use regex to extract the short ticker name   
    dividends_df['shortName'] = dividends_df.apply(lambda x: (re.findall("[A-Z]+", x['ticker'])[0]), axis = 1)   
    
    return dividends_df

def get_balance_df(api_key):
    """
    Function takes in the api key and returns a pandas dataframe of the 
    balances in the portfolio
    """
    
    # use function defined in api file to get portfolio balance data
    balance = api.get_balance(api_key)
    
    # convert balance dictionary into a pandas dataframe
    balance_df = pd.json_normalize(balance)
    
    # create percentage change column and portfolio value
    balance_df['pct_change'] = (balance_df['ppl'] / balance_df['invested']) * 100
    balance_df['portfolio_val'] = balance_df['total'] - balance_df['free']
    
    # rename columns so it is more intuitive
    rename_dict = {
        'total':'account_val',
        'ppl':'unrealised_gains',
        'result':'realised_gains'}
    
    balance_df = balance_df.rename(rename_dict, axis = 1)   
    
    balance_df = balance_df.round(2)

    return balance_df    

    
    
    
    
    
    
    
    
    
    
    
    
    
    