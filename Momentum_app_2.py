import streamlit as st
import yfinance as yf
import pandas_ta as ta
from openai import OpenAI



api_key = st.secrets["auth_token"]


client = OpenAI(api_key=api_key)

def main():

# Main application
    st.title("Stock Market Analysis with Technical Indicators")
    st.markdown("**Analyze stock trends using advanced technical indicators powered by AI.**")

    # Get user input for ticker symbol
    ticker = st.text_input("Enter Ticker Symbol", "", help="Enter the stock ticker symbol, e.g., 'AAPL' for Apple Inc.")
    st.subheader("Select a Timeframe for Analysis")

    timeframe = st.radio(
        "Select Timeframe:",
        ("1 Month", "3 Months", "6 Months", "1 Year"),
        horizontal=True
    )

    st.write("You selected:", timeframe)

    st.subheader("Select Analysis Type:")
    
    technical_analysis = st.checkbox("Technical Analysis")
    news_and_events = st.checkbox("News and Events")

    run_button = st.button("Run Analysis")

    progress_bar = st.progress(0)
    status_text = st.empty()

    if run_button:  # Check if the "Run" button is pressed
        if (technical_analysis or news_and_events) and timeframe:
            st.write(f"Analyzing data for the selected timeframe: {timeframe}")
            if timeframe == "1 Month":
                data = yf.download(ticker, period="1mo")
            elif timeframe == "3 Months":
                data = yf.download(ticker, period="3mo")
            elif timeframe == "6 Months":
                data = yf.download(ticker, period="6mo")
            elif timeframe == "1 Year":
                data = yf.download(ticker, period="1y")

            if technical_analysis and not news_and_events:
                st.write("Performing Technical Analysis...")
                
                # Check if data is empty
                if data.empty:
                    st.warning(f"No data available for {ticker}. Please check the ticker symbol and try again.")
                else:
                    update_progress(progress_bar, 10, 10, "Fetched stock data...")
                    
                    # Calculate technical indicators using pandas_ta
                    sma_available = False
                if 'Close' in data.columns:
                    data['SMA_20'] = ta.sma(data['Close'], length=20)
                    data['SMA_50'] = ta.sma(data['Close'], length=50)
                    data['SMA_200'] = ta.sma(data['Close'], length=200)
                    if data[['SMA_20', 'SMA_50', 'SMA_200']].notna().any().any():
                        sma_available = True
                    else:
                        update_progress(progress_bar, 30, 30, "SMA is not available...")

                # Calculate RSI
                rsi_available = False
                if 'Close' in data.columns:
                    data['RSI'] = ta.rsi(data['Close'], length=14)
                    if 'RSI' in data.columns and data['RSI'].notna().any():
                        rsi_available = True
                    else:
                        update_progress(progress_bar, 30, 30, "RSI is not available...")

                # Calculate MACD
                macd_available = False
                macd = ta.macd(data['Close'])
                if macd is not None and 'MACD_12_26_9' in macd.columns and 'MACDs_12_26_9' in macd.columns and 'MACDh_12_26_9' in macd.columns:
                    data['MACD'] = macd['MACD_12_26_9']
                    data['MACD_signal'] = macd['MACDs_12_26_9']
                    data['MACD_hist'] = macd['MACDh_12_26_9']
                    macd_available = True
                    
                else:
                    update_progress(progress_bar, 30, 30, "MACD is not available...")

                # Calculate OBV
                obv_available = False
                if 'Close' in data.columns and 'Volume' in data.columns:
                    data['OBV'] = ta.obv(data['Close'], data['Volume'])
                    if 'OBV' in data.columns and data['OBV'].notna().any():
                        obv_available = True
                    else:
                        update_progress(progress_bar, 30, 30, "OBV is not available...")

                # Calculate ADX
                adx_available = False
                adx = ta.adx(data['High'], data['Low'], data['Close'])
                if adx is not None and 'ADX_14' in adx.columns:
                    data['ADX'] = adx['ADX_14']
                    adx_available = True
                    
                else:
                    update_progress(progress_bar, 30, 30, "ADX is not available...")

                # Calculate Bollinger Bands
                bbands_available = False
                bbands = ta.bbands(data['Close'], length=20, std=2)
                if bbands is not None and 'BBU_20_2.0' in bbands.columns and 'BBM_20_2.0' in bbands.columns and 'BBL_20_2.0' in bbands.columns:
                    data['upper_band'] = bbands['BBU_20_2.0']
                    data['middle_band'] = bbands['BBM_20_2.0']
                    data['lower_band'] = bbands['BBL_20_2.0']
                    bbands_available = True
                    
                else:
                    update_progress(progress_bar, 30, 30, "Bollinger Bands are not available...")

                    # Prepare data for each technical indicator
                recent_data = data
                bd_markdown = recent_data[["Open", "High", "Low", "Close", "Volume", "upper_band", "middle_band", "lower_band"]].to_markdown()
                sma_markdown = recent_data[["Open", "High", "Low", "Close", "SMA_20", "SMA_50", "SMA_200"]].to_markdown()
                rsi_markdown = recent_data[["Open", "High", "Low", "Close", "RSI"]].to_markdown()

                # If MACD is available, prepare MACD data
                if macd_available:
                    macd_markdown = recent_data[["Open", "High", "Low", "Close", "MACD", "MACD_signal", "MACD_hist"]].to_markdown()

                obv_markdown = recent_data[["Open", "High", "Low", "Close", "Volume", "OBV"]].to_markdown()
                adx_markdown = recent_data[["Open", "High", "Low", "Close", "ADX"]].to_markdown()

                update_progress(progress_bar, 60, 60, "Preparing data for AI analysis...")

                # Get analysis from OpenAI
                update_progress(progress_bar, 65, 65, "Bollinger Bands Analysis...")
                bd_result = bollingerbands(ticker, bd_markdown)
                update_progress(progress_bar, 70, 70, "SMA Analysis...")
                sma_result = SMA(ticker, sma_markdown)
                update_progress(progress_bar, 75, 75, "RSI Analysis...")
                rsi_result = RSI(ticker, rsi_markdown)
                update_progress(progress_bar, 85, 85, "MACD Analysis...")
                # Only call MACD analysis if MACD data is available
                if macd_available:
                    macd_result = MACD(ticker, macd_markdown)
                else:
                    macd_result = "MACD analysis not available."  
                update_progress(progress_bar, 87, 87, "OBV Analysis...")
                obv_result = OBV(ticker, obv_markdown)
                update_progress(progress_bar, 90, 90, "ADX Analysis...")
                adx_result = ADX(ticker, adx_markdown)
                update_progress(progress_bar, 95, 95, "Analyzing...")

                # Get summary
                summary = SUMMARY(ticker, bd_result, sma_result, rsi_result, macd_result, obv_result, adx_result)
                update_progress(progress_bar, 100, 100, "Analysis complete!")

                

                # Display the summary in the second column
                st.subheader(f"Summary for {ticker}")
                st.write(summary)

                # Use an expander to show detailed analysis for each indicator
                if bbands_available:
                    with st.expander("View Detailed Analysis for Bollinger Bands"):
                        st.write(bd_result)
                
                if sma_available:
                    with st.expander("View Detailed Analysis for SMA"):
                        st.write(sma_result)

                if rsi_available:
                    with st.expander("View Detailed Analysis for RSI"):
                        st.write(rsi_result)

                if macd_available:
                    with st.expander("View Detailed Analysis for MACD"):
                        st.write(macd_result)

                if obv_available:
                    with st.expander("View Detailed Analysis for OBV"):
                        st.write(obv_result)

                if adx_available:
                    with st.expander("View Detailed Analysis for ADX"):
                        st.write(adx_result)

                if st.button("Run Another Stock"):
                    analysis_complete = False
                    st.session_state.technical_analysis = False
                    st.session_state.news_and_events = False
                    st.session_state["1_month"] = False
                    st.session_state["3_months"] = False
                    st.session_state["6_months"] = False
                    st.session_state["1_year"] = False
                    st.experimental_rerun() 

            if news_and_events and not technical_analysis:
                st.write("Analyzing News and Events...")
                        # Add news and event analysis code here
                news_response = generate_company_news_message(ticker, timeframe)
                st.subheader(f"News and Events Analysis for {ticker} over the past {timeframe}")
                st.write(news_response)

                if st.button("Run Another Stock"):
                    analysis_complete = False
                    st.session_state.technical_analysis = False
                    st.session_state.news_and_events = False
                    st.session_state["1_month"] = False
                    st.session_state["3_months"] = False
                    st.session_state["6_months"] = False
                    st.session_state["1_year"] = False
                    st.experimental_rerun()
            
            if news_and_events and technical_analysis:
                st.write("Performing Technical Analysis 2...")
                
                # Check if data is empty
                if data.empty:
                    st.warning(f"No data available for {ticker}. Please check the ticker symbol and try again.")
                else:
                    update_progress(progress_bar, 5, 5, "Fetched stock data...")
                    
                    # Calculate technical indicators using pandas_ta
                    sma_available = False
                if 'Close' in data.columns:
                    data['SMA_20'] = ta.sma(data['Close'], length=20)
                    data['SMA_50'] = ta.sma(data['Close'], length=50)
                    data['SMA_200'] = ta.sma(data['Close'], length=200)
                    if data[['SMA_20', 'SMA_50', 'SMA_200']].notna().any().any():
                        sma_available = True
                    else:
                        update_progress(progress_bar, 10, 10, "SMA is not available...")

                # Calculate RSI
                rsi_available = False
                if 'Close' in data.columns:
                    data['RSI'] = ta.rsi(data['Close'], length=14)
                    if 'RSI' in data.columns and data['RSI'].notna().any():
                        rsi_available = True
                    else:
                        update_progress(progress_bar, 15, 15, "RSI is not available...")

                # Calculate MACD
                macd_available = False
                macd = ta.macd(data['Close'])
                if macd is not None and 'MACD_12_26_9' in macd.columns and 'MACDs_12_26_9' in macd.columns and 'MACDh_12_26_9' in macd.columns:
                    data['MACD'] = macd['MACD_12_26_9']
                    data['MACD_signal'] = macd['MACDs_12_26_9']
                    data['MACD_hist'] = macd['MACDh_12_26_9']
                    macd_available = True
                    
                else:
                    update_progress(progress_bar, 20, 20, "MACD is not available...")

                # Calculate OBV
                obv_available = False
                if 'Close' in data.columns and 'Volume' in data.columns:
                    data['OBV'] = ta.obv(data['Close'], data['Volume'])
                    if 'OBV' in data.columns and data['OBV'].notna().any():
                        obv_available = True
                    else:
                        update_progress(progress_bar, 25, 25, "OBV is not available...")

                # Calculate ADX
                adx_available = False
                adx = ta.adx(data['High'], data['Low'], data['Close'])
                if adx is not None and 'ADX_14' in adx.columns:
                    data['ADX'] = adx['ADX_14']
                    adx_available = True
                    
                else:
                    update_progress(progress_bar, 30, 30, "ADX is not available...")

                # Calculate Bollinger Bands
                bbands_available = False
                bbands = ta.bbands(data['Close'], length=20, std=2)
                if bbands is not None and 'BBU_20_2.0' in bbands.columns and 'BBM_20_2.0' in bbands.columns and 'BBL_20_2.0' in bbands.columns:
                    data['upper_band'] = bbands['BBU_20_2.0']
                    data['middle_band'] = bbands['BBM_20_2.0']
                    data['lower_band'] = bbands['BBL_20_2.0']
                    bbands_available = True
                    
                else:
                    update_progress(progress_bar, 35, 35, "Bollinger Bands are not available...")

                    # Prepare data for each technical indicator
                recent_data = data
                bd_markdown = recent_data[["Open", "High", "Low", "Close", "Volume", "upper_band", "middle_band", "lower_band"]].to_markdown()
                sma_markdown = recent_data[["Open", "High", "Low", "Close", "SMA_20", "SMA_50", "SMA_200"]].to_markdown()
                rsi_markdown = recent_data[["Open", "High", "Low", "Close", "RSI"]].to_markdown()

                # If MACD is available, prepare MACD data
                if macd_available:
                    macd_markdown = recent_data[["Open", "High", "Low", "Close", "MACD", "MACD_signal", "MACD_hist"]].to_markdown()

                obv_markdown = recent_data[["Open", "High", "Low", "Close", "Volume", "OBV"]].to_markdown()
                adx_markdown = recent_data[["Open", "High", "Low", "Close", "ADX"]].to_markdown()

                update_progress(progress_bar, 40, 40, "Preparing data for AI analysis...")

                # Get analysis from OpenAI
                update_progress(progress_bar, 45, 45, "Bollinger Bands Analysis...")
                bd_result = bollingerbands(ticker, bd_markdown)
                update_progress(progress_bar, 50, 50, "SMA Analysis...")
                sma_result = SMA(ticker, sma_markdown)
                update_progress(progress_bar, 55, 55, "RSI Analysis...")
                rsi_result = RSI(ticker, rsi_markdown)
                update_progress(progress_bar, 60, 60, "MACD Analysis...")
                # Only call MACD analysis if MACD data is available
                if macd_available:
                    macd_result = MACD(ticker, macd_markdown)
                else:
                    macd_result = "MACD analysis not available."  
                update_progress(progress_bar, 65, 65, "OBV Analysis...")
                obv_result = OBV(ticker, obv_markdown)
                update_progress(progress_bar, 70, 70, "ADX Analysis...")
                adx_result = ADX(ticker, adx_markdown)
                update_progress(progress_bar, 80, 80, "Analyzing...")

                # Get summary
                summary = SUMMARY(ticker, bd_result, sma_result, rsi_result, macd_result, obv_result, adx_result)
                update_progress(progress_bar, 85, 85, "Technical Analysis complete!")

                st.write("Analyzing News and Events...")
                        # Add news and event analysis code here
                news_response = generate_company_news_message(ticker, timeframe)
                update_progress(progress_bar, 90, 90, "Nearly Finished!")
                ovr_summary = merge_news_and_technical_analysis_summary(ticker,news_response,summary)
                update_progress(progress_bar, 100, 100, "Analysis complete!")
                st.subheader(f"News and Events Analysis and Technical Analysis for {ticker} over the past {timeframe}")
                st.write(ovr_summary)

                if st.button("Run Another Stock"):
                    analysis_complete = False
                    st.session_state.technical_analysis = False
                    st.session_state.news_and_events = False
                    st.session_state["1_month"] = False
                    st.session_state["3_months"] = False
                    st.session_state["6_months"] = False
                    st.session_state["1_year"] = False
                    st.experimental_rerun()
                  
        
                
                    
        else:
            st.warning("Please select at least one analysis type to proceed.")

    #if t_col1.button("Technical Analysis"):
        #analysis_type = "Technical Analysis"
    #elif n_col2.button("News and Events"):
        #analysis_type = "News and Events"

    

    
   



def merge_news_and_technical_analysis_summary(company_name, news_summary, technical_summary):
    """
    Combines the news and events summary with the technical analysis summary using OpenAI's GPT model.
    
    Parameters:
    - company_name: The name of the company being analyzed.
    - news_summary: The summarized news and events information.
    - technical_summary: The summarized technical analysis output.

    Returns:
    - An overall summary that integrates both the news and technical analysis in a cohesive manner.
    """
    # OpenAI API call to create a merged summary
    chat_completion = client.chat.completions.create(
        model="gpt-4o",  # Ensure that you use a model available in your OpenAI subscription
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI assistant that helps traders and investors make decisions by analyzing market data. "
                    "Your goal is to merge news and events with technical analysis to create a comprehensive summary that provides "
                    "actionable insights. The summary should be clear, concise, and include an overview of both the fundamental aspects (news) "
                    "and technical trends of the stock. Focus on the overall overview and actionable recommendations"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Please create a combined summary for the company {company_name} using the following information:\n\n"
                    f"News and Events Summary:\n{news_summary}\n\n"
                    f"Technical Analysis Summary:\n{technical_summary}\n\n"
                    "Merge these details into one cohesive summary, highlighting how the news may impact the stock's technical indicators and providing "
                    "an overall outlook on the stock's potential future performance."
                ),
            },
        ]
    )

    # Extract and return the AI-generated response
    response = chat_completion.choices[0].message.content
    return response

def generate_company_news_message(company_name, time_period):
    # Define the messages for different time periods 
          
    chats = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an artificial intelligence assistant, and your role is to "
                    f"provide the latest news and updates for {company_name} in a detailed, organized, and engaging manner."
            },
            {
                "role": "user",
                "content": f"Can you share the latest news and events of {company_name} over the past {time_period}?"
            },
        ]
    )
    response = chats.choices[0].message.content
    return response
     

def bollingerbands(company_name, data_text):
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an AI model designed to assist long-term day traders in analyzing stock market data. "
                    "Your primary task is to interpret stock trading data, especially focusing on Bollinger Bands, "
                    "to identify key market trends. When provided with relevant data you will: "
                    "Analyze the stock's current position relative to its Bollinger Bands (upper, middle, or lower bands) and provide insights."
            },
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
    time.sleep(5)
    st.empty()

def merge_news_and_technical_analysis_summary(company_name, news_summary, technical_summary):
    """
    Combines the news and events summary with the technical analysis summary using OpenAI's GPT model.
    
    Parameters:
    - company_name: The name of the company being analyzed.
    - news_summary: The summarized news and events information.
    - technical_summary: The summarized technical analysis output.

    Returns:
    - An overall summary that integrates both the news and technical analysis in a cohesive manner.
    """
    # OpenAI API call to create a merged summary
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Ensure that you use a model available in your OpenAI subscription
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI assistant that helps traders and investors make decisions by analyzing market data. "
                    "Your goal is to merge news and events with technical analysis to create a comprehensive summary that provides "
                    "actionable insights. The summary should be clear, concise, and include an overview of both the fundamental aspects (news) "
                    "and technical trends of the stock."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Please create a combined summary for the company {company_name} using the following information:\n\n"
                    f"News and Events Summary:\n{news_summary}\n\n"
                    f"Technical Analysis Summary:\n{technical_summary}\n\n"
                    "Merge these details into one cohesive summary, highlighting how the news may impact the stock's technical indicators and providing "
                    "an overall outlook on the stock's potential future performance."
                ),
            },
        ]
    )

    # Extract and return the AI-generated response
    response = chat_completion.choices[0].message.content
    return response




if __name__=="__main__":
    main()
