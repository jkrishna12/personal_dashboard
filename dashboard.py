import streamlit as st
import return_dataframes as rd
import crypto
from plots import dashboard_plot as dplt
from plots import position_plot as pplt
from plots import dividend_plot as div_plt

@st.cache_data(ttl = '15minutes')
# @st.cache_data()
def load_data(t212_api_key):
    """
    Function takes in api key and returns portfolio, balance and 
    dividend dataframe
    """
    
    portfolio_df = rd.get_clean_portfolio_df(t212_api_key)
    balance_df = rd.get_balance_df((t212_api_key))
    dividends_df = rd.get_dividends_df(t212_api_key)
    
    crypto_df, etoro_cash_gbp = crypto.etoro_variables_init()
    
    
    return portfolio_df, balance_df, dividends_df, crypto_df, etoro_cash_gbp

def color_positive_or_negative(value):
    color = "red" if value < 0 else "green"
    return f"color: {color};"


st.set_page_config(
    page_title='Finance Dashboard',
    layout='wide'
    )

# st.set_option('deprecation.showPyplotGlobalUse', False)


st.title('Finance Dashboard')

if 't212_input' not in st.session_state:
    st.session_state['t212_input'] = ''
    
t212_api_key = st.text_input('Enter the Trading212 Api Key', value = '', key = 't212_input')

st.write('loading data can take some time')

if st.session_state['t212_input'] != '': 

    portfolio_df, balance_df, dividends_df, crypto_df, etoro_cash_gbp = load_data(t212_api_key)       
    
    dashboard_tab, pos_tab, dividend_tab = st.tabs(['Dashboard', 'Position', 'Dividends'])
        
    with dashboard_tab:
        
        st.subheader('Key Numbers')
        
        dashboard_col1_1, dashboard_col1_2 = st.columns(2)
        
        account_val, portfolio_val, cash, invested, unrealised_gains, pct = dplt.print_values(balance_df, crypto_df, etoro_cash_gbp)
        
        with dashboard_col1_1:
            
            st.write(f"**Account Value:** £{account_val:.2f}")
            st.write(f"**Portfolio Value:** £{portfolio_val:.2f}")
            st.write(f"**Cash:** £{cash:.2f}")   
        
        with dashboard_col1_2:
            
            st.write(f"**Invested:** £{invested}")
            
            if balance_df['unrealised_gains'][0] >= 0:
                st.write(f"**Unrealised Gains:** :green[£{unrealised_gains:.2f}({pct}%)]")
            else:
                st.write(f"**Unrealised Gains:** :red[£{unrealised_gains:.2f}({pct}%)]")
            
            if balance_df['realised_gains'][0] >= 0:
                st.write(f"**Realised Gains:** :green[£{balance_df['realised_gains'][0]}]")    
            else:
                st.write(f"**Realised Gains:** :red[£{balance_df['realised_gains'][0]}]")
                    
        st.divider()
        
        dashboard_col2_1, dashboard_col2_2 = st.columns([0.33,0.66])
        
        with dashboard_col2_1:
            st.subheader("Portfolio Breakdown")

            option = st.selectbox('Pick General or Detailed Breakdown',
                                  ['General', 'Detailed'])
            
            pie_balance = dplt.pie_balance_breakdown(portfolio_df, crypto_df, etoro_cash_gbp, balance_df, option)            

            st.plotly_chart(pie_balance, use_container_width=True,
                            theme = 'streamlit')
            
        with dashboard_col2_2:
            
            st.subheader('Portfolio Change')
            
            option = st.selectbox('Pick Percentage Change or Absolute Value Change',
                                  ['Percent Change', 'Absolute Value Change'])
            
            figure = dplt.portfolio_position_breakdown(portfolio_df, crypto_df, option)
            
            # st.pyplot(figure)
            
            st.plotly_chart(figure, use_container_width=True,
                            theme = 'streamlit')
    
    
    with pos_tab:
        portfolio_df_show = pplt.load_position_df(portfolio_df, crypto_df)
        
        styled_df = portfolio_df_show.style.map(color_positive_or_negative,
                                                     subset=['Value Change (GBP)', 'Percentage Change'])            
        
        st.dataframe(styled_df.format(precision = 2),                                  
                     use_container_width=True,
                     hide_index = True)
        
    with dividend_tab:
        
        st.subheader('Dividends Paid Out')
        
        total = dividends_df['amount'].sum()
        
        st.write(f"**Total:** £{total:.2f}")
        
        entries = st.slider('Entries Displayed:', min_value=1, max_value = 10, 
                  value = 5, step = 1)
        
        div_hist = div_plt.dividend_history(dividends_df, entries = entries)
        
        st.dataframe(div_hist, use_container_width=False, hide_index = True)
        
        st.divider()
        
        year_bar_fig, month_bar_fig = div_plt.dividend_bar_plot(dividends_df)
        
        dividend_col1_1, dividend_col1_2 = st.columns(2)
        
        with dividend_col1_1:
            st.subheader('Yearly Dividend Pay Out')
            st.plotly_chart(year_bar_fig, use_container_width=True,
                            theme = 'streamlit')
            
        with dividend_col1_2:
            st.subheader('Year to Date Monthly Dividend Payout')
            st.plotly_chart(month_bar_fig, use_container_width=True,
                            theme = 'streamlit')
            
        st.divider()
        
        st.subheader('Historic Stock Dividend Payout')
        
        stock_option = st.selectbox('Pick a stock', list(dividends_df['shortName'].unique()))
        
        stock_fig, stock_paid_out = div_plt.specific_stock_df(dividends_df, stock_option)
           
        if stock_fig != None:
        
            st.write(f"**Total Amount Paid Out:** £{stock_paid_out}")        
    
            # st.pyplot(stock_fig, use_container_width = False)      
            
            st.plotly_chart(
                stock_fig,
                use_container_width=True,                
                theme = 'streamlit'
                )
            
        else:
                      
            st.write(f"**Total Amount Paid Out:** £{stock_paid_out} (only 1 payout)")

            
                       
    













