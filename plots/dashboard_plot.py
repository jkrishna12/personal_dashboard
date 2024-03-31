import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go



def pie_plot_matplotlib(df, label):
    """
    Takes in a dataframe and returns a pie chart
    
    Paramters:
        df: Pandas Dataframe
        label: String, column name to annotate the pie chart
    Return:
        fig: Matplotlib Figure, Figure of pie chart
    """
    
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
    
    fig.set_facecolor('#0E1117')
    
    explode = np.full(len(df), 0.1)
    
    wedges, texts = ax.pie(df['currentPos'], 
                           wedgeprops=dict(width=0.5),
                           startangle=0,
                          colors=sns.color_palette('Set2', len(df)),
                          explode = explode)
    
    # bbox_props = dict(boxstyle="square,pad=0.1", fc="w", ec="k", lw=0.72)
    
    # kw = dict(arrowprops=dict(arrowstyle="-"),
    #           bbox=bbox_props, zorder=0, va="center")
    
    kw = dict(arrowprops=dict(arrowstyle="-"),
              zorder=0, va="center")
    
    for i, p in enumerate(wedges):
        
        # if statement ensures that holdings greater than 1% are shown
        if df.loc[i, 'pct'] > 1:
        
            ang = (p.theta2 - p.theta1)/2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = f"angle,angleA=0,angleB={ang}"
            
            kw["arrowprops"].update({"connectionstyle": connectionstyle, 'color':'white'})
            ax.annotate(f"{df.loc[i, label]}, {df.loc[i, 'pct']}%", xy=(x, y), xytext=(1.4*np.sign(x), 1.4*y),
                        horizontalalignment=horizontalalignment,
                        color = 'white', **kw)
    
    return fig

def pie_plot_plotly(df, label):
    """
    Function returns a plotly pie chart figure
    
    Parameters:
        df: Pandas Dataframe, dataframe of the account
        label: String, column axis, determines whether detailed or general breakdown is returned
    Returns:
        fig: plotly Figure, general/detailed pie chart figure
    """
    
    fig = go.Figure(data = go.Pie(values = df['currentPos'],
                               labels = df[label],
                               hole = 0.5,
                              pull = np.full(len(df), 0.1),
                              showlegend = False))
    
    fig.update_traces(textinfo = 'label+percent',
                  hoverinfo = 'label+value')
    
    if label == 'shortName':
        title = 'Detailed'
    else:
        title = 'General'
    
    fig.update_layout(width=500, height=500, title = f"Portfolio {title} Breakdown")
    
    # fig.title(f"{label} Breakdown")
    
    return fig


def pie_balance_breakdown(portfolio_df, crypto_df, etoro_cash, balance_df, option):
    """
    Function takes in the portfolio and balance dataframes and returns 
    a breakdown of the positions in the form of a pie chart
    
    Parameters:
        portfolio_df: Pandas Dataframe, of portfolio dataframe
        crypto_df: Pandas Dataframe, of crypto dataframe
        etoro_cash: Integer, etoro cash in gbp
        balance_df: Pandas Dataframe, of balance dataframe
        option: String, Depending on the opiton different pie chart will be returned
        
    Returns:
        instrument_fig: Matplotlib figure, pie chart depdning on the option argument
    """
    
    # selecting only relevant columns from portfolio dataframe
    portfolio_df = portfolio_df[['shortName', 'type', 'currentPos']]
    
    # selecting only relevant columns from crypto dataframe
    crypto_df = crypto_df[['shortName', 'type', 'currentPos']]
        
    # select the current cash from the balance df and create a Dataframe in the 
    # same form as the portfolio dataframe 
    balance_df_concat = pd.DataFrame({'shortName':'Cash','type':'Cash', 'currentPos':balance_df['free'] + etoro_cash})
    
    # concatenate the balance_df_concat with the portfolio_df
    account_df = pd.concat([portfolio_df, crypto_df, balance_df_concat])
    
    if option == 'Detailed':
    
        # sort values and reset index
        account_df = account_df.sort_values('currentPos', ascending = False)
        account_df.reset_index(inplace = True, drop = True)
        
        # holding_fig = pie_plot_matplotlib(account_df, 'shortName')
        holding_fig = pie_plot_plotly(account_df, 'shortName')
        
        return holding_fig
        
    elif option == 'General':
        # group the instruments by the type
        account_df_groupby = account_df.groupby('type')['currentPos'].sum().reset_index()
       
        instrument_fig = pie_plot_plotly(account_df_groupby, 'type')
        
        return instrument_fig
        
    
def bar_plot_matplotlib(df, fig_option, x_axis, y_axis, x_label, y_label):
    """
    Function takes in a dataframe and axis and label paramters and returns a
    bar figure
    Parameters:
        df: Pandas Dataframe
        fig_option: String
        x_axis: String, column name of df
        y_axis: String, column name of df
        x_label: String, label of the x axis
        y_label: String, label of the y axis
    Returns:
        fig: Matplotlib figure, figure of bar chart
    """
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.set_facecolor('#0E1117')
    fig.set_facecolor('#0E1117')
    ax.spines[['right', 'top']].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    
    # sns.set_palette('Set2', len(df))

    sns.barplot(data = df, x = x_axis, y = y_axis, palette = 'Set2', ax = ax)
    
    ax.set(xlabel = x_label, ylabel = y_label)
    
    ax.tick_params(axis='x', rotation=45, colors = 'w')
    
    ax.tick_params(axis='y', colors = 'w')
    
    # ax.grid(True, axis = 'y', alpha = 0.2, color = 'w')
    
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    
    for bar in ax.patches:

      # Using Matplotlib's annotate function and
      # passing the coordinates where the annotation shall be done
      # x-coordinate: bar.get_x() + bar.get_width() / 2
      # y-coordinate: bar.get_height()
      # free space to be left to make graph pleasing: (0, 8)
      # ha and va stand for the horizontal and vertical alignment
        
        if bar.get_height() < 0:
            height = 1
        else:
            height = bar.get_height()
        
        ax.annotate(format(bar.get_height(), '.2f'), 
                       (bar.get_x() + bar.get_width() / 2, 
                        height), ha='center', va='center',
                       size=8, xytext=(0, 8),
                       textcoords='offset points', color = 'white')
        
    ax.set_title(f"Portfolio {fig_option}", color = 'white')    
    
    return fig 

def bar_plot_plotly(df, fig_option, x_axis, y_axis, x_label, y_label):
    """
    Function takes the portfolio dataframe and returns a bar graph of either the 
    value change or percentage change
    Parameters:
        df: Pandas Dataframe, portfolio dataframe
        fig_option: String, determines whether value change or percentage change graph is shown
        x_axis: String, column label to plot on x axis
        y_axis: String, column label to plot on y axis
        x_label: String, x axis label
        y_label: String, y axis label
    Return:
        fig: Plotly figure, bar chart
    """
    

    
    fig = go.Figure(data = [go.Bar(
            x = df[x_axis], y = df[y_axis],
            text = df[y_axis],
            textposition='outside',
            hovertemplate = '%{x}: %{y:.2f} <extra></extra>')])
    
    if fig_option == 'Absolute Value Change':
        fig.update_traces(texttemplate='£%{text}')
    else:
        fig.update_traces(texttemplate='%{text}%')
        
    
    fig.update_layout(width=500, height=500,
                      xaxis_tickangle = -45, title = f"Portfolio {fig_option}",
                      xaxis_title = x_label, yaxis_title = y_label)
    
    
    return fig


def portfolio_position_breakdown(portfolio_df, crypto_df, fig_option):
    """
    Function takes in the portfolio dataframe and returns a bar chart of the 
    value or percentage change depending on the figure option
    Paramters:
        portfolio_df: Pandas Dataframe, of portfolio dataframe
        crypto_df: Pandas Dataframe of crypto dataframe
        fig_option: String, dictates what breakdown is returned
    Returns:
        fig_year: Matplotlib Figure, either percentage change bar chart or 
                 absolute value change bar chart depending on fig option
    """
   
    account_df = pd.concat([portfolio_df, crypto_df])
   
    x_axis = 'shortName'
    x_label = 'Ticker'
    
    if fig_option == 'Percent Change':      
        
        y_axis = 'pct_change'
        y_label = 'Percentage Change'
        
        # fig_year = bar_plot_matplotlib(portfolio_df, fig_option, x_axis, y_axis,
        #                     x_label, y_label)
        
        fig_year = bar_plot_plotly(account_df, fig_option, x_axis, y_axis, x_label, y_label)
        
        return fig_year
        
    elif fig_option == 'Absolute Value Change':
        
        y_axis = 'abs_value_change'
        y_label = 'Absolute Value Change (£)'
           
        fig_year = bar_plot_plotly(account_df, fig_option, x_axis, y_axis,
                            x_label, y_label)
        
        return fig_year
    
    
def print_values(balance_df, crypto_df, etoro_cash):
    
    crypto_invested = crypto_df['origPos'].sum()
    crypto_portfolio = crypto_df['currentPos'].sum()
    
    
    account_val = balance_df['account_val'][0] + crypto_portfolio + etoro_cash
    portfolio_val = np.round(balance_df['portfolio_val'][0] + crypto_portfolio,2)
    cash = balance_df['free'][0] + etoro_cash
    
    invested = balance_df['invested'][0] + crypto_invested
    
    unrealised_gains = balance_df['unrealised_gains'][0] + (crypto_portfolio - crypto_invested)
    
    pct = np.round(((portfolio_val - invested) / invested) * 100, 2)
    
    
    return account_val, portfolio_val, cash, invested, unrealised_gains, pct





















