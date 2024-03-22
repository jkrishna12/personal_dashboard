import pandas as pd

def load_position_df(portfolio_df, crypto_df):
    """
    Function takes in the portfolio dataframe and returns a dataframe with the
    relevant columns
    Paramters:
        portfolio_df: Pandas Dataframe, portfolio dataframe
    Returns:
        portfolio_df_copy: Pandas Dataframe, copy of the portfolio dataframe
                           selecting the relevant renamed columns
    
    """
    # copies the portfolio_df
    portfolio_df_copy = portfolio_df.copy()
    
    # copies the crypto df
    crypto_df_copy = crypto_df.copy()
    
    cols_order = ['name', 'shortName', 'quantity',
                   'averagePrice_GBP', 'currentPrice_GBP',
                   'currentPos', 'abs_value_change',
                   'pct_change']
    
    # selecting only the relevant columns of portfolio df
    portfolio_df_copy = portfolio_df_copy[cols_order]
    
    # selecting only the relevant columns of crypto df
    crypto_df_copy = crypto_df_copy[cols_order]
    
    # concatenate portfolio and crypto dataframes
    account_df = pd.concat([portfolio_df_copy, crypto_df_copy], ignore_index=True)
    
    
    # dictionary to rename columns
    rename_dict = {
                    'name':'Name',
                    'shortName':'Ticker',
                    'quantity':'Shares',
                    'averagePrice_GBP':'Average Price (GBP)',
                    'currentPrice_GBP':'Current Price (GBP)',
                    'currentPos':'Current Position',
                    'abs_value_change':'Value Change (GBP)',
                    'pct_change':'Percentage Change'
        }
    
    # rename the columns
    account_df.rename(columns = rename_dict, inplace = True)
    
    
    return account_df

