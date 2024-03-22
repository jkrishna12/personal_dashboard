import requests
import re
import time

def get_portfolio(api_key):
    """
    Function takes in the api key and returns a json variable of all the 
    positions in the portfolio
    """
    # url of the website
    url = "https://live.trading212.com/api/v0/equity/portfolio"
    
    # headers dictionary containing API key pass to requests get
    headers = {"Authorization": f"{api_key}"}
    
    # try block will request the data 
    try:
        response = requests.get(url, headers=headers)   
        data = response.json() 
        return data   
    except requests.exceptions.RequestException as e:
        print(f'Unable to pull portfolio data due to {response}')
        print(e)
        return None
        
    
def get_instrument_data(api_key):
    """
    Function takes in the api key and returns json data of all the instruments available
    """
    # instrument url pulling data from
    url_instruments = "https://live.trading212.com/api/v0/equity/metadata/instruments"
    
    # headers dictionary containing API key to pass to requests get 
    headers_instruments = {"Authorization": api_key}    
    
    # try block will request the data
    
    try:
        response_instruments = requests.get(url_instruments, headers=headers_instruments)
        data_instrument = response_instruments.json()
        
        return data_instrument
    except requests.exceptions.RequestException as e:
        print(f'Unable to pull instrument data due to {response_instruments}')
        print(e)
        return None
    
def get_transaction(api_key):   
    """
    Function takes in the api key and returns a json list of dictionaries of 
    all the transactions that have taken place
    """
    # url of the website
    url = "https://live.trading212.com/api/v0/history/transactions"
    
    # header dictionary containing the api key
    headers = {"Authorization": f"{api_key}"}
    
    # transaction dictionary whill contain all of the items
    transactions = {'items':[]}
    
    # these variables are empty strings whill will change depending on the page of a list
    next_page_cursor = ''
    time_param = ''
    limit = 20
    
    # while loop continues iterating until it reaches the end of the list
    while True:
        # condition checks whether items in transaction list is equal to 0
        # depending on condition of statement it will change the cursor position and time param
        if len(transactions['items']) == 0:
            query = {'limit': '20'}

        else:
            query = {'cursor': f"{next_page_cursor}", 'time':f"{time_param}", 'limit': f"{limit}"}
        
        # try block requests data from website
        try:
            response = requests.get(url, headers = headers, params = query)
            data = response.json()
        
        # except block raises error if error produced
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
            
        print(response, response.ok)
        # print(data)
        
        # if condition put loop to sleep for 61 seconds if too many requests were made
        while response.status_code == 500:
            
            # puts function to sleep for 61 seconds
            time.sleep(61)
            
            # after elapsed time will request data
            response = requests.get(url, headers = headers, params = query)
            data = response.json()
            
            print(response, response.ok)
            
        if 'errorMessage' in response:
            errorMessage = response['errorMessage']
            print(errorMessage)
            time.sleep(61)
            response = requests.get(url, headers=headers, params=query)
            response = response.json()
            
        # extends the transaction items by the new data 
        transactions['items'].extend(data['items'])
        
        # conditions dictate whether to continue with the loop and assign new cursor position and time parameter
        # or will exit the while loop
        if data['nextPagePath'] is not None:
            
            next_page_cursor = re.findall("cursor=(.*)&", data['nextPagePath'])[0]
            
            time_param = re.findall("time=(.*)", data['nextPagePath'])[0]
            
        else:
            break
        
        # returns the list of dictionaries of all the transactions
    return transactions['items']

def get_dividends(api_key):
    """
    Function takes in the api key and returns a list of dictionaries of the dividends paid out
    """
    # url to request data from 
    url = "https://live.trading212.com/api/v0/history/dividends"
    
    # headers dictionary containing the api key
    headers = {"Authorization": f"{api_key}"}
    
    # empty dictionary which will store the items key, list of dividends paid out, 
    # nextPagePath, string of the next page 
    dividends = {'items': [], 'nextPagePath': ""}
    
    # loop allows continuous requesting of dividend data
    while True:
        # if else statements sets the query dictionary depending on the position of the cursor
        if len(dividends["items"]) == 0:
            query = {"cursor": "", "ticker": "", "limit": "50"}
        else: 
            query = {"cursor": f"{dividends['nextPagePath']}", "ticker": "", "limit": "50"}
            
        # try except block allows requesting of data otherwise will raise error
        try:
            response = requests.get(url, headers=headers, params=query)
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
            
        # if too many requests are made loop is put to sleep for 61 seconds before requesting again
        if 'errorMessage' in response:
            errorMessage = response['errorMessage']
            print(errorMessage)
            time.sleep(61)
            response = requests.get(url, headers=headers, params=query)
            data = response.json()
        
        # extends the dividends items list with the new data 
        dividends['items'].extend(data['items'])
        
        # if statement checks whether there is more data to extract 
        # if there is updates the dividends['nextPagePath'] with the new page string
        if data['nextPagePath'] is not None:
            cursor_string = re.findall("cursor=(.*)", data['nextPagePath'])[0]
            dividends['nextPagePath'] = cursor_string
        # if there isn't a new cursor break the loop
        else:
            break
            
    # returns the dividend item list
    return dividends["items"]

def get_balance(api_key):
    """
    Function takes in the api key and returns a dictionary of the balances
    in the portfolio
    """
    
    # url of the cash balances 
    url = "https://live.trading212.com/api/v0/equity/account/cash"
    
    # header dictionary containing the api key
    headers = {"Authorization": f"{api_key}"}
    
    # requesting the balance data
    response = requests.get(url, headers=headers)
    
    # assign portfolio balances to data
    data = response.json()
    
    return data
            
    
    
    
    
    
    
    