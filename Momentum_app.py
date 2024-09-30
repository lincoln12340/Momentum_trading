import streamlit as st
import pandas as pd
import yfinance as yf
import talib
import matplotlib.pyplot as plt
from openai import OpenAI




client = OpenAI(api_key="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")

def bollingerbands(company_name,data_text):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data. "
                    "Your primary task is to interpret stock trading data, especially focusing on Bollinger Bands, "
                    "to identify key market trends. When provided with relevant data you will: "
                    "\n\n- Analyze the stock's current position relative to its Bollinger Bands (upper, middle, or lower bands)."
                    "\n- Assess if the stock is in an uptrend, downtrend, or nearing a breakout."
                    "\n- Determine if the stock is prone to a reversal based on price movements, volatility, and Bollinger Band contraction or expansion."
                    "\n- Provide a concise, expert-level explanation of your analysis, including how specific Bollinger Band characteristics (e.g., squeeze, volatility changes, band width) "
                    "indicate potential market moves."
                    "\n\nEnsure that your explanations are clear and easy to understand, even for users with little to no trading experience, avoiding complex jargon or offering simple definitions where necessary. "
                    "Your output should balance depth and simplicity, offering actionable insights for traders while being accessible to non-traders."
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing the Bollinger Bands?"
                
            },
        ]
    )

    response = chat_completion.choices[0].message.content
    return response


def SMA(company_name,data_text):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data."
                    "Your primary task is to interpret stock trading data, especially focusing on 20, 50, and 200 Simple Moving Averages (SMA),"
                    "to identify key market trends. When provided with relevant data you will:"
                    "\n- Analyze the stock's current position relative to its 20, 50, and 200 SMAs."
                    "\n- Assess if the stock is in an uptrend, downtrend, or nearing a breakout based on the relationships between the SMAs."
                    "\n- Determine if the stock is prone to a reversal by analyzing price movements, SMA crossovers, and the stock's position relative to key SMAs."
                    "\n- Provide a concise, expert-level explanation of your analysis, including how specific SMA characteristics (e.g., crossovers, price deviation from SMAs, trend strength)"
                    "indicate potential market moves."
                    "\n\nEnsure that your explanations are clear and easy to understand, even for users with little to no trading experience, avoiding complex jargon or offering simple definitions where necessary."
                    "Your output should balance depth and simplicity, offering actionable insights for traders while being accessible to non-traders."
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing SMA?"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response


def RSI(company_name,data_text):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data."
                    "Your primary task is to interpret stock trading data, especially focusing on the Relative Strength Index (RSI),"
                    "to identify key market trends. When provided with relevant data you will:"

                    "\n- Analyze the stock's current RSI values to determine if it is overbought, oversold, or in a neutral range."
                    "\n- Assess if the stock is in an uptrend, downtrend, or nearing a potential reversal based on RSI levels and patterns."
                    "\n- Determine if the stock is prone to a reversal by analyzing RSI divergences (bullish or bearish), overbought/oversold conditions, and the stock's momentum."
                    "\n- Provide a concise, expert-level explanation of your analysis, including how specific RSI characteristics (e.g., divergence, trend strength, threshold breaches)"
                    "indicate potential market moves."
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing RSI?"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response

def MACD(company_name,data_text):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data."
                    "Your primary task is to interpret stock trading data, especially focusing on the MACD (Moving Average Convergence Divergence), MACD Signal Line, and MACD Histogram,"
                    "to identify key market trends. When provided with relevant data you will:"
                    "\n- Analyze the stock's MACD line, Signal Line, and Histogram to assess trend strength and potential price direction."
                    "\n- Assess if the stock is in an uptrend, downtrend, or nearing a crossover by analyzing the MACD line relative to the Signal Line."
                    "\n- Determine if the stock is prone to a reversal by examining MACD crossovers, divergences, and changes in the MACD Histogram."
                    "\n- Provide a concise, expert-level explanation of your analysis, including how specific MACD characteristics (e.g., crossover points, divergence, histogram changes)"
                    "indicate potential market moves."
                    "\n\nEnsure that your explanations are clear and easy to understand, even for users with little to no trading experience, avoiding complex jargon or offering simple definitions where necessary."
                    "Your output should balance depth and simplicity, offering actionable insights for traders while being accessible to non-traders."
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing MACD?"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response


def OBV(company_name,data_text):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data."
                    "Your primary task is to interpret stock trading data, especially focusing on On-Balance Volume (OBV),"
                    "to identify key market trends. When provided with relevant data you will:"

                    "\n\n- Read and extract relevant data from PDF and CSV files."
                    "\n- Analyze the stock's OBV to assess the relationship between volume and price movement."
                    "\n- Assess if the stock is in an uptrend, downtrend, or nearing a breakout by evaluating OBV trends and volume momentum."
                    "\n- Determine if the stock is prone to a reversal by analyzing OBV divergences (where OBV moves in the opposite direction of price), which can signal potential trend changes."
                    "\n- Provide a concise, expert-level explanation of your analysis, including how specific OBV characteristics (e.g., divergence, volume spikes, confirmation of price moves)"
                    "indicate potential market moves."

                    "\n\nEnsure that your explanations are clear and easy to understand, even for users with little to no trading experience, avoiding complex jargon or offering simple definitions where necessary."
                    "Your output should balance depth and simplicity, offering actionable insights for traders while being accessible to non-traders."
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing the OBV?"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response


def ADX(company_name,data_text):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data."
                    "Your primary task is to interpret stock trading data, especially focusing on the Average Directional Index (ADX),"
                    "to identify key market trends. When provided with relevant data you will:"

                    "\n- Analyze the stock's ADX values to assess the strength of the current trend, regardless of its direction."
                    "\n- Assess if the stock is in a strong or weak trend based on ADX levels, with particular attention to rising or falling ADX values."
                    "\n- Determine if the stock is prone to a trend reversal by analyzing ADX indicating whether the market is gaining or losing trend strength."
                    "\n- Provide a concise, expert-level explanation of your analysis, including how specific ADX characteristics (e.g., ADX crossovers, trend strength, or weakening trends)"
                    "indicate potential market moves."

                    "\n\nEnsure that your explanations are clear and easy to understand, even for users with little to no trading experience, avoiding complex jargon or offering simple definitions where necessary."
                    "Your output should balance depth and simplicity, offering actionable insights for traders while being accessible to non-traders."
                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please analyze the stock data for {company_name}, here is the data {data_text}, What insights can you provide from observing ADX?"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response

def SUMMARY(company_name,BD,SMA,RSI,MACD,OBV,ADX):
    
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an AI model designed to assist long-term day traders in analyzing stock market data."
                    "Your primary task is to interpret and provide a well-rounded conclusion from texts that report on both lagging indicators (MACD, SMA) and leading indicators (ADX, RSI, OBV, Bollinger Bands),"
                    "to offer clear and easy-to-understand insights on the trend of the stock. When provided with relevant data you will:"

                    "\n\n- Read and extract key information from texts or reports that discuss MACD, SMA (lagging indicators), and ADX, RSI, OBV, Bollinger Bands (leading indicators)."
                    "\n- Synthesize the findings from multiple sources into a cohesive conclusion, drawing connections between the behaviors of lagging and leading indicators."
                    "\n- Provide a clear and concise conclusion about the stock's overall trend, including whether it is strengthening, weakening, or showing signs of a reversal based on the combined data."
                    "\n- Offer insights into the likely future direction of the stock by interpreting the interactions between lagging and leading indicators (e.g., MACD crossover with RSI overbought/oversold conditions)."

                    "\n\nEnsure that your conclusions are clear and easy to understand, assume the person reading has no idea about trading, avoiding complex jargon where necessary."
                    "Your output should balance depth and simplicity, offering actionable insights for traders while being accessible to non-traders."
                    "Only output the end conclusion no need to output the individual insights from each indicator"
                    "Limit the output to just 1 paragraph"
                    "Give Very Simple Advice of what long term position one should take based of the analysis and bold it"
                    
                   
                                    
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"Please summarise the stock data for {company_name}, here is the text for Bollinger bands: {BD}, Simple Moving Averages: {SMA}, Relative Strength Index: {RSI}, MACD: {MACD}, OBV: {OBV}, ADX: {ADX}"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response

def update_progress(progress_bar, stage, progress, message):
    progress_bar.progress(progress)
    st.text(message)


# Main application
st.title("Stock Market Analysis with Technical Indicators")
st.markdown("**Analyze stock trends using advanced technical indicators powered by AI.**")

# Get user input for ticker symbol
ticker = st.text_input("Enter Ticker Symbol", "", help="Enter the stock ticker symbol, e.g., 'AAPL' for Apple Inc.")

# Set up a progress bar and column layout
progress_bar = st.progress(0)
status_text = st.empty()

# Display input fields and progress side by side
col1, col2 = st.columns(2)

if ticker:
    # Fetch historical data for the last year
    data = yf.download(ticker, period="1y")
    update_progress(progress_bar, 10, 10, "Fetched stock data...")
    

    # Calculate technical indicators
    data['SMA_20'] = talib.SMA(data['Close'], timeperiod=20)
    data['SMA_50'] = talib.SMA(data['Close'], timeperiod=50)
    data['SMA_200'] = talib.SMA(data['Close'], timeperiod=200)
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
    data['MACD'], data['MACD_signal'], data['MACD_hist'] = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    data['OBV'] = talib.OBV(data['Close'], data['Volume'])
    data['ADX'] = talib.ADX(data['High'], data['Low'], data['Close'], timeperiod=14)
    data['upper_band'], data['middle_band'], data['lower_band'] = talib.BBANDS(data['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    update_progress(progress_bar, 40, 40, "Calculated technical indicators...")

    # Prepare data for each technical indicator
    recent_data = data.tail(30)
    bd_markdown = recent_data[["Open", "High", "Low", "Close", "Volume", "upper_band", "middle_band", "lower_band"]].to_markdown()
    sma_markdown = recent_data[["Open", "High", "Low", "Close", "SMA_20", "SMA_50", "SMA_200"]].to_markdown()
    rsi_markdown = recent_data[["Open", "High", "Low", "Close", "RSI"]].to_markdown()
    macd_markdown = recent_data[["Open", "High", "Low", "Close", "MACD", "MACD_signal", "MACD_hist"]].to_markdown()
    obv_markdown = recent_data[["Open", "High", "Low", "Close", "Volume", "OBV"]].to_markdown()
    adx_markdown = recent_data[["Open", "High", "Low", "Close", "ADX"]].to_markdown()
    update_progress(progress_bar, 60, 60, "Prepared data for AI analysis...")

    # Get analysis from OpenAI
    bd_result = bollingerbands(ticker, bd_markdown)
    sma_result = SMA(ticker, sma_markdown)
    rsi_result = RSI(ticker, rsi_markdown)
    macd_result = MACD(ticker, macd_markdown)
    obv_result = OBV(ticker, obv_markdown)
    adx_result = ADX(ticker, adx_markdown)
    update_progress(progress_bar, 80, 80, "Analysing...")

    # Get summary
    summary = SUMMARY(ticker, bd_result, sma_result, rsi_result, macd_result, obv_result, adx_result)
    update_progress(progress_bar, 100, 100, "Analysis complete!")

    # Display the summary in the second column
    st.subheader(f"Summary for {ticker}")
    st.write(summary)

    # Use an expander to show detailed analysis for each indicator
    with st.expander("View Detailed Analysis for Bollinger Bands"):
        st.write(bd_result)
    
    with st.expander("View Detailed Analysis for SMA"):
        st.write(sma_result)

    with st.expander("View Detailed Analysis for RSI"):
        st.write(rsi_result)

    with st.expander("View Detailed Analysis for MACD"):
        st.write(macd_result)

    with st.expander("View Detailed Analysis for OBV"):
        st.write(obv_result)

    with st.expander("View Detailed Analysis for ADX"):
        st.write(adx_result)

else:
    st.info("Please enter a valid ticker symbol to begin the analysis.")