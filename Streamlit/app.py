import streamlit as st

import yfinance as yf

from yahooquery import search

from datetime import date, timedelta

import plotly.graph_objects as go

import plotly.express as px

from plotly.subplots import make_subplots 

import matplotlib.pyplot as plt
import pandas as pd

from stock_model import model_train

def get_input() -> pd.DataFrame :
    try:
        search_type = st.radio('Search by:', ('Ticker', 'Company Name'))
        
        ticker = set_ticker(search_type)
        if not ticker:
            st.warning("Please enter a valid ticker symbol.")
            return None
        else:
            return load_data(ticker)
    except Exception as e:
        st.error(f"Error occurred: {e}")
        
def set_ticker(search_type) -> yf.ticker :
    
    if search_type =="Ticker":
        ticker = st.text_input("Enter the Ticker of A Stock", 'AAPL')  
    else:
        comp= st.text_input("Enter the Company Name", 'Apple Inc.') 
        
        ticker=search_comp(comp)
    return ticker
        
#function to retrive the ticker of a Company
def search_comp(company_name) -> yf.ticker:

    search_result = search(company_name)

    if search_result['quotes']:
        st.write("Search results For the Company name:")
        for i, item in enumerate(search_result['quotes'], start=1):
            st.write(f"{i}. Symbol: {item['symbol']}, Name: {item['shortname']}, Exchange: {item['exchange']}")
            
        # Dynamically generate the list of options for the selectbox
        options = list(range(1, len(search_result['quotes']) + 1))
        choice = st.selectbox("Select the number corresponding to the correct ticker symbol:", options)    
        
        ticker = search_result['quotes'][choice - 1]['symbol']
        st.write(ticker)
        if st.button("Enter"):
            return ticker 


def load_data(ticker) -> pd.DataFrame:
    try:        
        stock_data = yf.download(ticker,period='ytd',interval='1d') 
       # stock_data=stock_data.drop(['Dividends','Stock Splits'],axis=1)
        
        # Example of fetching data for a custom date range:
        # stock_data = yf.download(ticker, start=start_date, end=end_date)
        return stock_data
    except Exception as e:
        st.error(f"Failed to fetch data for {ticker}. Error: {e}")
        return None
def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    st.subheader("Filter Stock Price by Month")

    # Ensure 'Date' is the index and reset it to a column for easier filtering
    df = df.reset_index()

    # Create a dropdown to select the month
    months = df['Date'].dt.strftime('%B').unique()
    month = st.selectbox("Select Month", months)

    # Filter the dataframe based on the selected month
    filtered_df = df[df['Date'].dt.strftime('%B') == month]

    # Calculate the price range within the selected month
    price_min = filtered_df['Close'].min()
    price_max = filtered_df['Close'].max()

    # Display the price range
    st.write(f"Price range for {month}: {price_min} - {price_max}")

    st.write(filtered_df)

def line_plot(stock_data) -> None:
    fig=plt.figure(figsize=(10, 5))
    plt.plot(stock_data['Close'], label='Price')

    #setting up the title and labels
    plt.title("Price Movement Of Stock")
    plt.xlabel('Year')
    plt.ylabel('Price')
    
    plt.grid(True)

    plt.legend()
    st.pyplot(fig)
    #plt.show()

def candlesticks_plot(df) -> None:
    #creating the past 1 year data for plotting and observation 
    #df = df.iloc[-365:]  # yf.download(ticker_symbol, start=start_date,end=end_date, progress=False)
    
    

    df["Date"] = df.index

    df = df[["Date", "Open", "High", "Low", "Close",  "Volume"]]

    #df.reset_index(drop=True, inplace=True)
    #plotting the data in Candlesticks which is differntiates the Increase and decrease in price
    figure = go.Figure(data=[go.Candlestick(x=df["Date"],
                                        open=df["Open"], 
                                        high=df["High"],
                                        low=df["Low"], 
                                        close=df["Close"],
                                        increasing_line_color='green', 
                                        decreasing_line_color='red',
                                        increasing_fillcolor='green',
                                        decreasing_fillcolor='red')])

    figure.update_layout(title = " Stock Price Movement Upto Today", xaxis_rangeslider_visible=False)

    figure.update_xaxes(
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=3, label="3m", step="month", stepmode="backward"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    )
)

    figure.update_layout(title = "Stock Price Analysis Upto Today", 
                     xaxis_rangeslider_visible=True,height=700,width=1100)

    st.plotly_chart(figure)
    #figure.show()

def plot_price_volume(data) -> None:
        #line chart of date and close
    #last two years of data
    df=data[-730:]
    
    figure = px.line(df, x='Date', y='Close',title='Stock Market Analysis with Time Period Selectors For the Past Two years')
    
    figure.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    # Update trace to change line color
    figure.update_traces(line=dict(color='blue'))
    
    #plotting both 
    figure.update_layout(yaxis2=dict(title="Price",overlaying='y',side="right"),height=700,width=1100)
    
    #changing the volume in minimum amount for representtion
    for i in range(1,df.size):
        volume =df["Volume"]/1000000
    
    figure.add_trace(
        go.Bar(x=df["Date"],  # X-axis data (dates)
        y=df["Volume"] / 1000000,  # Y-axis data (volume in Lakhs)
        name="Trading Volume in Lakhs",  # Legend label
        marker=dict(color='red'),  # Specify the bar color here
        yaxis='y2' , # Use secondary y-axis for volume
    ))
    
    figure.update_layout(
        yaxis=dict(title="Price"),  # Primary y-axis title
        yaxis2=dict(title="Volume (Lakhs)", overlaying='y', side="right"),  # Secondary y-axis title and position
        height=700,
        width=1100, #increasing the size of plotting
        bargap=0.5,   # Gap between bars
        bargroupgap=0.1  # Gap between groups of bars
    )
    
    #figure.show()
    st.plotly_chart(figure)

def prediction(stock_data):
    st.subheader("Prediction Of A next Day Stock")
    actual,predicted=model_train(stock_data,stock_data)
    if st.button("Predict") :
                 st.write(f"Actual Value is {actual}")
                 st.write(f"Predicted Value {predicted}")
        
if __name__ == "__main__":
       
    st.title('Stock Forecast App')
    
    stock_data = get_input()   
    
    if stock_data is not None and not stock_data.empty:
        st.subheader("Price and Volume Information Of The Entered Stock:")
        reverse=stock_data.iloc[::-1]
        st.write(reverse)
        filter_data(stock_data)
        
        prediction(stock_data)
        
        candlesticks_plot(stock_data)
        line_plot(stock_data)
        plot_price_volume(stock_data)
    else:
        st.warning("No valid data to display.")
