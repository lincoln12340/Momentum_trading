import streamlit as st
import yfinance as yf
import pandas_ta as ta
from openai import OpenAI
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import tempfile
import os 


api_key = st.secrets["auth_token"]


client = OpenAI(api_key=api_key)


def main():

# Main application
    st.set_page_config(page_title="Stock Market Analysis", layout="wide", page_icon="📈")

    # Sidebar with interactive options
    with st.sidebar:
        st.title("Market Analysis Dashboard")
        st.markdown("Analyze stock trends using advanced technical indicators powered by AI.")
        
        # Ticker Input
        ticker = st.text_input(" Enter Ticker Symbol", "", help="Example: 'AAPL' for Apple Inc.")
        company = st.text_input(" Enter Full Company Name", "", help="Example: 'Apple Inc.'")
        
        # Timeframe Selection
        st.subheader("Select Timeframe for Analysis")
        timeframe = st.radio(
            "Choose timeframe:",
            ("1 Month", "3 Months", "6 Months", "1 Year"),
            index=3,
            help="Select the period of historical data for the stock analysis"
        )
        
        # Analysis Type Selection
        st.subheader("Analysis Options")
        technical_analysis = st.checkbox("Technical Analysis", help="Select to run technical analysis indicators")
        news_and_events = st.checkbox("News and Events", help="Get recent news and event analysis for the company")
        fundamental_analysis = st.checkbox("Fundamental Analysis", help="Select to upload a file for fundamental analysis")

        uploaded_file = None
        if fundamental_analysis:
            uploaded_file = st.file_uploader("Upload a PDF file for Fundamental Analysis", type="pdf")
        
        # Run Button with styled alert text
        run_button = st.button("Run Analysis")
        st.markdown("---")
        st.info("Click 'Run Analysis' after selecting options to start.")

    # Main content section
    st.title("Stock Market Analysis with AI-Powered Insights")
    st.markdown("**Gain actionable insights into stock trends with advanced indicators and AI interpretations.**")

    progress_bar = st.progress(0)
    status_text = st.empty()

    if run_button:
         
        if timeframe == "1 Month":
            data = yf.download(ticker, period="1mo")
        elif timeframe == "3 Months":
            data = yf.download(ticker, period="3mo")
        elif timeframe == "6 Months":
            data = yf.download(ticker, period="6mo")
        elif timeframe == "1 Year":
            data = yf.download(ticker, period="1y")  # Check if the "Run" button is pressed
        
      
        
        if not technical_analysis and not news_and_events and not fundamental_analysis:
            st.warning("Please select at least one analysis type to proceed.")
        if data.empty:
            st.warning(f"No data available for {ticker}. Please check the ticker symbol and try again.")
        if not company:
            st.warning(f" Please add Name of company.")
        elif technical_analysis:
            with st.expander("Downloading Data"):
                st.write(f"Analyzing data for the selected timeframe: {timeframe}")
                st.write("Performing Technical Analysis...")       # Check if data is empty
                update_progress(progress_bar, 10, 10, "Fetched stock data...")        
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
                
                data = data.resample('W').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum',
                    'SMA_20': 'last',
                    'SMA_50': 'last',
                    'SMA_200': 'last',
                    'RSI': 'last',
                    'MACD': 'last',
                    'MACD_signal': 'last',
                    'MACD_hist': 'last',
                    'OBV': 'last',
                    'ADX': 'last',
                    'upper_band': 'last',
                    'middle_band': 'last',
                    'lower_band': 'last'
                })

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
                # Get summar
                update_progress(progress_bar, 100, 100, "Analysis complete!")

            if technical_analysis and not news_and_events and not fundamental_analysis:
                summary = SUMMARY(ticker, bd_result, sma_result, rsi_result, macd_result, obv_result, adx_result)
                st.subheader(f"Summary for {ticker}")
                st.write(summary)

                # Use an expander to show detailed analysis for each indicator
                if bbands_available:
                    with st.expander("View Detailed Analysis for Bollinger Bands"):
                        fig_bbands = plot_bbands(data)
                        st.plotly_chart(fig_bbands)
                        st.write(bd_result)  # Display Bollinger Bands result or interpretation

                if sma_available:
                    with st.expander("View Detailed Analysis for SMA"):
                        fig_sma = plot_sma(data)
                        st.plotly_chart(fig_sma)
                        st.write(sma_result)  # Display SMA result or interpretation

                if rsi_available:
                    with st.expander("View Detailed Analysis for RSI"):
                        fig_rsi = plot_rsi(data)
                        st.plotly_chart(fig_rsi)
                        st.write(rsi_result)  # Display RSI result or interpretation

                if macd_available:
                    with st.expander("View Detailed Analysis for MACD"):
                        fig_macd = plot_macd(data)
                        st.plotly_chart(fig_macd)
                        st.write(macd_result)  # Display MACD result or interpretation

                if obv_available:
                    with st.expander("View Detailed Analysis for OBV"):
                        fig_obv = plot_obv(data)
                        st.plotly_chart(fig_obv)
                        st.write(obv_result)  # Display OBV result or interpretation

                if adx_available:
                    with st.expander("View Detailed Analysis for ADX"):
                        fig_adx = plot_adx(data)
                        st.plotly_chart(fig_adx)
                        st.write(adx_result)  # Display ADX result or interpretation

                if st.button("Run Another Stock"):
                    analysis_complete = False
                    st.session_state.technical_analysis = False
                    st.session_state.news_and_events = False
                    st.session_state["1_month"] = False
                    st.session_state["3_months"] = False
                    st.session_state["6_months"] = False
                    st.session_state["1_year"] = False
                    st.experimental_rerun() 

            if news_and_events and not technical_analysis and fundamental_analysis:
                txt_summary = generate_company_news_message(company, timeframe)
                txt_summary = format_news(txt_summary)
                txt_ovr = txt_conclusion(txt_summary,company)
                        
                st.subheader(f"News and Events Analysis for {ticker} over the past {timeframe}")
                st.write(txt_summary)
                st.write(txt_ovr)

                if st.button("Run Another Stock"):
                    analysis_complete = False
                    st.session_state.technical_analysis = False
                    st.session_state.news_and_events = False
                    st.session_state["1_month"] = False
                    st.session_state["3_months"] = False
                    st.session_state["6_months"] = False
                    st.session_state["1_year"] = False
                    st.experimental_rerun()

            if news_and_events and technical_analysis and not fundamental_analysis:
                summary = SUMMARY(ticker, bd_result, sma_result, rsi_result, macd_result, obv_result, adx_result)
                txt_summary = generate_company_news_message(company, timeframe)
                txt_summary = format_news(txt_summary)
                txt_ovr = txt_conclusion(txt_summary,company)
                ovr_summary = merge_news_and_technical_analysis_summary(company,txt_summary,summary,timeframe)

                st.subheader(f"News and Events Analysis and Technical Analysis for {ticker} over the past {timeframe}")
                st.write(txt_summary)
                st.subheader("Technical Analysis Summary")
                st.write(summary)
                st.subheader("Overall Summary")
                st.write(ovr_summary)
                st.subheader("Detailed Technical Analysis")

                if bbands_available:
                    with st.expander("View Detailed Analysis for Bollinger Bands"):
                        fig_bbands = plot_bbands(data)
                        st.plotly_chart(fig_bbands)
                        st.write(bd_result)  # Display Bollinger Bands result or interpretation

                if sma_available:
                    with st.expander("View Detailed Analysis for SMA"):
                        fig_sma = plot_sma(data)
                        st.plotly_chart(fig_sma)
                        st.write(sma_result)  # Display SMA result or interpretation

                if rsi_available:
                    with st.expander("View Detailed Analysis for RSI"):
                        fig_rsi = plot_rsi(data)
                        st.plotly_chart(fig_rsi)
                        st.write(rsi_result)  # Display RSI result or interpretation

                if macd_available:
                    with st.expander("View Detailed Analysis for MACD"):
                        fig_macd = plot_macd(data)
                        st.plotly_chart(fig_macd)
                        st.write(macd_result)  # Display MACD result or interpretation

                if obv_available:
                    with st.expander("View Detailed Analysis for OBV"):
                        fig_obv = plot_obv(data)
                        st.plotly_chart(fig_obv)
                        st.write(obv_result)  # Display OBV result or interpretation

                if adx_available:
                    with st.expander("View Detailed Analysis for ADX"):
                        fig_adx = plot_adx(data)
                        st.plotly_chart(fig_adx)
                        st.write(adx_result)  # Display ADX result or interpretation

                if st.button("Run Another Stock"):
                    analysis_complete = False
                    st.session_state.technical_analysis = False
                    st.session_state.news_and_events = False
                    st.session_state["1_month"] = False
                    st.session_state["3_months"] = False
                    st.session_state["6_months"] = False
                    st.session_state["1_year"] = False
                    st.experimental_rerun()    
            if fundamental_analysis and not technical_analysis and not news_and_events: 
                file_content = uploaded_file
                file_name = uploaded_file.name
                fa_summary = FUNDAMENTAL_ANALYSIS(file_content, company, file_name)
                st.subheader(f"Fundamental Analysis for {ticker} over the past {timeframe}")
                st.write(fa_summary)
            
            if fundamental_analysis and technical_analysis and not news_and_events:

                file_content = uploaded_file
                file_name = uploaded_file.name
                fa_summary = FUNDAMENTAL_ANALYSIS(file_content, company, file_name)
                summary = SUMMARY(ticker, bd_result, sma_result, rsi_result, macd_result, obv_result, adx_result)
                fa_ta_summary = merge_ta_fa_summary(fa_summary,summary)
                #st.subheader(f"Fundamental Analysis and Technical Analysis for {ticker} over the past {timeframe}")
                st.write(fa_ta_summary)


            if fundamental_analysis and news_and_events and not news_and_events: 
                txt_summary = generate_company_news_message(company, timeframe)
                txt_summary = format_news(txt_summary)
                txt_ovr = txt_conclusion(txt_summary,company)
                ovr_summary = merge_news_and_technical_analysis_summary(company,txt_summary,summary,timeframe)

                file_content = uploaded_file
                file_name = uploaded_file.name
                fa_summary = FUNDAMENTAL_ANALYSIS(file_content, company, file_name)

                fa_txt_summary = fa_summary_and_news_summary(fa_summary,ovr_summary)
                st.write(fa_txt_summary)





def fa_summary_and_news_summary(fa_summary, txt_summary):

           
    chat_completion = client.chat.completions.create(
        model="gpt-4o",  # Ensure that you use a model available in your OpenAI subscription
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI model trained to create a comprehensive investment report by integrating recent news and events data with fundamental analysis. Your role is to merge insights from an asset's financial health with the impact of current developments to produce a well-rounded assessment and actionable recommendations. Use the following format and guidelines to structure your response:"
                    "\n\n"
                    "Formatting Requirements:\n"
                    "- **Headings and Subheadings**: Organize the report with clear headings (e.g., “Fundamental Analysis Summary,” “Recent News and Events,” “Investment Insights”).\n"
                    "- **Consistent Formatting**: Bold critical metrics and key event names (e.g., **Revenue Growth**, **Product Launch**), and use italics for qualitative insights (*e.g., regulatory implications*, *market sentiment*).\n"
                    "- **Bullet Points and Numbered Lists**: Use bullet points for lists of events and data points, and numbered lists for any recommended steps or prioritized actions.\n\n"
                    
                    "Structure Guidelines:\n"
                    "1. **Introduction**:\n"
                    "   - Briefly summarize the asset, its industry context, and the relevance of both fundamental analysis and recent events.\n"
                    "   - State the objective: to integrate fundamental performance with recent news for a complete perspective on the asset's investment potential.\n\n"

                    "2. **Fundamental Analysis Summary**:\n"
                    "   - **Financial Performance**: Summarize key financial metrics (e.g., revenue growth, net income) reflecting the asset’s stability.\n"
                    "   - **Valuation Metrics**: Include metrics like Price-to-Earnings (P/E) ratio, Price-to-Book (P/B) ratio, Dividend Yield, with industry comparisons.\n"
                    "   - **Market Position and Competitive Standing**: Outline the asset’s market position, competitive strengths, and a brief SWOT summary.\n"
                    "   - **Key Takeaways**: Summarize the overall financial health and growth outlook.\n\n"

                    "3. **Recent News and Events Summary**:\n"
                    "   - **Recent Developments**: Summarize major events impacting the asset (e.g., product launches, regulatory changes).\n"
                    "   - **Market Sentiment and Impact**: Describe how each event has affected market sentiment, whether positively or negatively.\n"
                    "   - **Macro and Industry-Level News**: Include any broader economic or industry-specific developments relevant to the asset.\n"
                    "   - **Key Takeaways**: Highlight the potential influence of recent events on the asset’s outlook.\n\n"

                    "4. **Integrated Investment Insights**:\n"
                    "   - **Alignment of Fundamentals with Recent Events**: Describe how recent events support or challenge the asset’s fundamental outlook.\n"
                    "   - **Market Sentiment vs. Intrinsic Value**: Evaluate the alignment of current sentiment with the asset’s intrinsic value.\n"
                    "   - **Risk Factors**: Identify any risks that recent events may introduce, such as regulatory risks or changes in competitive positioning.\n\n"

                    "5. **Actionable Recommendations**:\n"
                    "   - **Investment Decision**: Provide a recommendation (Buy, Hold, Sell), considering both fundamental and recent event insights.\n"
                    "   - **Entry and Exit Points**: Suggest entry/exit levels based on news and valuation metrics.\n"
                    "   - **Risk Management and Monitoring**: Recommend any risk management strategies and important future events or updates to track.\n\n"

                    "Style Requirements:\n"
                    "- Maintain a professional, data-driven tone without personal opinions.\n"
                    "- Minimize jargon, and briefly clarify terms where necessary.\n"
                    "- Keep sentences and paragraphs clear and concise to maintain logical flow and readability."
                    
                    "Using these instructions, deliver a concise, actionable report combining news, events, and fundamental analysis for strategic investment decision-making."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"From and merge these texts, Recent News and Events: {txt_summary} and Fundamental Analysis: {fa_summary}"
                ),
            },
        ]
    )



                


                
                



def merge_ta_fa_summary(fa_summary,ta_summary):

    chat_completion = client.chat.completions.create(
        model="gpt-4o",  # Ensure that you use a model available in your OpenAI subscription
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI model designed to provide comprehensive, long-term investment analysis by merging fundamental and technical analysis. Your role is to combine insights from financial health, competitive positioning, and market trends with technical indicators to deliver actionable, data-driven recommendations tailored for long-term investment strategies. Use the following structure and formatting guidelines to provide a detailed and practical report:"
                    "Formatting Requirements:"
                    "Organized Headings and Subheadings: Use clear headings and subheadings to separate sections (e.g., “Long-Term Financial Overview,” “Technical Indicators for Trend Analysis,” “Long-Term Investment Recommendations”)."
                    "Bullet Points and Numbered Lists: Use bullet points for lists and numbered lists for prioritized or sequential steps, especially in recommendation sections."
                    "Formatting for Key Metrics and Indicators:"
                    "Bold critical financial terms and technical indicators (e.g., Net Profit Margin, Relative Strength Index (RSI))."
                    "Use italics for qualitative insights (e.g., market trends, strategic risks)."
                    "Data Presentation: Use tables or charts to compare financial metrics over time and to track changes in technical indicators, where appropriate, for easy reference."
                    "Structure Guidelines:"
                    "Introduction:"
                    "Briefly summarize the asset’s profile, market sector, and relevance for long-term investors."
                    "Highlight the objective of integrating fundamental strength with technical trend analysis to support long-term holding decisions."
                    "Fundamental Analysis:"
                    "Financial Performance and Stability: Examine key financial statements (income statement, balance sheet, and cash flow) to evaluate profitability, solvency, and growth. Focus on metrics that support stability, such as revenue growth, earnings stability, and debt management.Valuation Metrics: Highlight ratios relevant to long-term value (e.g., Price-to-Earnings (P/E), Price-to-Book (P/B), and Dividend Yield) and compare them to industry averages."
                    "Competitive Position and Market Standing: Assess the asset’s market share, competitive advantages, and potential risks. Include a SWOT analysis to illustrate long-term growth drivers and potential challenges."
                    "Technical Analysis for Long-Term Trend:"
                    "Key Indicators for Long-Term Trends:"
                    "MACD (Moving Average Convergence Divergence): Examine long-term trends by focusing on signal line crossovers and divergence from the price to identify trend strength."
                    "ADX (Average Directional Index): Use ADX to measure trend strength (with readings above 20 typically indicating a strong trend). Specify whether a strong uptrend or downtrend is evident."
                    "On-Balance Volume (OBV): Analyze OBV to determine if volume trends align with price trends, confirming potential long-term price direction."
                    "Bollinger Bands: Use Bollinger Bands to identify volatility and potential entry points when the price approaches the upper or lower bands over longer timeframes."
                    "Relative Strength Index (RSI): Focus on RSI values over extended periods to determine if the asset is overbought or oversold, guiding long-term entry or exit points."
                    "Simple Moving Averages (SMA) (e.g., 50-day, 200-day): Track crossovers between SMAs to identify long-term bullish or bearish trends (e.g., a “golden cross” when the 50-day SMA rises above the 200-day SMA)."
                    "Integrated Analysis:"

                    "Correlation of Fundamental Strength with Technical Trends: Discuss how the asset’s intrinsic value and financial health align with its technical trend, focusing on consistency or divergence between long-term value indicators and current market trends."
                    "Market Sentiment and Timing Implications: Summarize how technical signals (e.g., RSI, ADX, MACD) align with long-term valuation and growth potential. Highlight any discrepancies between market sentiment and intrinsic value for timing entry points."
                    "Long-Term Actionable Recommendations:"
                    "Investment Decision: Clearly state a Buy, Hold, or Sell recommendation, backed by fundamental and technical indicators. For example, if financial metrics are strong and technical indicators signal a bullish trend, recommend a Buy with specific reasons."
                    "Entry and Exit Points: Identify ideal entry points based on long-term technical indicators (e.g., price touching lower Bollinger Band in an uptrend or RSI below 30 in a fundamentally strong asset)."
                    "Risk Management Strategies: Outline risk mitigation techniques suitable for long-term investors, such as setting a stop-loss level based on SMA trends or diversifying within the sector to reduce exposure."
                    "Performance Monitoring for Long-Term: List key fundamental updates (e.g., quarterly earnings) and technical indicators (e.g., changes in ADX, MACD crossovers) to monitor periodically for alignment with the long-term outlook."
                    "Style Requirements:"
                    "Maintain a professional, analytical tone, avoiding personal opinions."
                    "Minimize jargon, explaining technical terms in plain language where necessary for clarity."
                    "Keep sentences and paragraphs concise, ensuring the report remains readable and logically structured for a long-term investment context."
                    "Using these instructions, you will deliver a detailed, actionable report that enables readers to make well-informed, strategic investment decisions based on an integrated approach to fundamental and technical analysis."
                                        #Add Press releases, investor oppinions (X), First World Pharma, Bloomberg, Market Watch, seperate segment,add sources, add graphs
                    
                ),
            },
            {
                "role": "user",
                "content": (
                    f"From and merge these texts, Technical Analysis: {ta_summary} and Fundamental Analysis: {fa_summary}"
                ),
            },
        ]
    )

    # Extract and return the AI-generated response
    response = chat_completion.choices[0].message.content
    return response

                        
                

        #if t_col1.button("Technical Analysis"):
            #analysis_type = "Technical Analysis"
        #elif n_col2.button("News and Events"):
            #analysis_type = "News and Events"

def txt_conclusion(news_summary,company_name):
    # OpenAI API call to create a merged summary
    chat_completion = client.chat.completions.create(
        model="gpt-4o",  # Ensure that you use a model available in your OpenAI subscription
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI model specializing in investment insights, tasked with analyzing recent news and events about a specified company and providing recommendations for investors. Your goal is to review relevant data, including press releases, market trends, earnings reports, and industry events, to assess the companys financial health, growth prospects, and potential risks. From this data, you will determine an ideal investor position (e.g., buy, hold, or sell)."
                    "Instructions:"
                    "Data Collection: Search for and analyze recent press releases, earnings reports, regulatory filings, and news articles regarding the specified company. Focus on the following:"
                    "Financial Performance: Look for quarterly or annual earnings, revenue, and profit trends."
                    "Product & Service Developments: Identify any new product launches, service expansions, or market innovations."
                    "Management Statements: Note key statements from executives or significant personnel changes that might impact the companys direction."
                    "Industry Events & Competitor Actions: Examine news of industry-wide developments, competitor performance, and market conditions."
                    "Regulatory & Legal News: Assess any legal challenges, regulatory updates, or policy changes impacting the company."
                    "Sentiment Analysis: Evaluate the tone and sentiment of the news data—whether positive, neutral, or negative. Gauge investor confidence and sentiment trends as reflected in the media."
                    "Market Impact: Summarize any immediate or anticipated effects of recent events on the companys stock price, including short-term volatility, potential growth indicators, or risk factors that could affect long-term performance."
                    "Investor Recommendation:"
                    "Buy: Recommend if positive news, strong financial performance, and promising growth potential outweigh risks."
                    "Hold: Suggest if there are mixed indicators, with potential growth tempered by risks or uncertain factors."
                    "Sell: Advise if significant risks, declining performance, or negative news dominate, suggesting potential for downturn."
                    "Final Conclusion: Provide a clear summary and reasoning behind the recommended position, addressing key data points and highlighting the rationale for an investor's action."
                    "Additional Sources: A separate section listing sources like press releases and opinions from the mentioned platforms, ensuring proper citations."
                    #Add Press releases, investor oppinions (X), First World Pharma, Bloomberg, Market Watch, seperate segment,add sources, add graphs
                    
                ),
            },
            {
                "role": "user",
                "content": (
                    f"News and Events Summary for {company_name}:\n{news_summary}\n\n"   
                ),
            },
        ]
    )

# Extract and return the AI-generated response
    response = chat_completion.choices[0].message.content
    return response 

    

def merge_news_and_technical_analysis_summary(company_name, news_summary,technical_summary,time_period):
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
                    "As an AI assistant dedicated to supporting traders and investors in their decision-making processes, your primary objective is to synthesize relevant market data by merging current news and events with thorough technical analysis.  "
                    "Begin by analyzing the latest market news, focusing particularly on economic indicators, press releases, and significant announcements that may influence stock performance. Simultaneously, evaluate technical trends, including price movements, volume patterns, and key indicators (such as moving averages and RSI) for the selected stock. "
                    "Once you have gathered and analyzed this information, compile a comprehensive summary that is clear and concise. This summary should include a detailed overview of both the fundamental aspects, highlighting impactful news, and the technical trends that characterize the stock's movement."
                    "Following this, present an elaborate and focused overall assessment that includes actionable recommendations based on anticipated future news and historical trends. "
                    "In addition to the main summary, create a separate segment that includes insights from various sources such as press releases, investor opinions, First World Pharma, Bloomberg, and Market Watch. Ensure that you properly cite all sources used to enhance credibility and allow for further investigation."
                    "Structure the output as follows: 1.Introduction: Brief overview of the stock and its relevance in the current market context. 2. News Analysis: Summary of significant news and events affecting the stock."
                    "3. Technical Analysis: Insights on price movements and relevant technical indicators. 4. Comprehensive Summary: A synthesis of the news and technical analysis, along with actionable recommendations."
                    "Additional Sources: A separate section listing sources like press releases and opinions from the mentioned platforms, ensuring proper citations."
                    #Add Press releases, investor oppinions (X), First World Pharma, Bloomberg, Market Watch, seperate segment,add sources, add graphs
                    
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Please create a combined summary for the company {company_name} using the following information:\n\n"
                    f"News and Events Summary:\n{news_summary}\n\n"
                    f"Technical Analysis Summary:\n{technical_summary}\n\n"
                    "Merge these details into one cohesive summary, make it flow, highlighting how the news may impact the stock's technical indicators and providing "
                    f"an in-depth overall outlook on the stock's potential future performance for the next coming {time_period}, plus provide actionable recommendations as well."
                ),
            },
        ]
    )

    # Extract and return the AI-generated response
    response = chat_completion.choices[0].message.content
    return response

def generate_company_news_message(company_name, time_period):
    # Define the messages for different time periods 
    def post_to_webhook(data):
        webhook_url = "https://hook.eu2.make.com/s4xsnimg9v87rrrckcwo88d9k57186q6"
        if webhook_url:
    
            response = requests.post(webhook_url,data)
            return response
        else:
            print("Error")

    data = {"Ticker": company_name, "Time Frame": time_period}


    response = post_to_webhook(data)
    print(response.text)

    time.sleep(65)

    scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

    credentials_dict = {
        "type": st.secrets["google_credentials"]["type"],
        "project_id": st.secrets["google_credentials"]["project_id"],
        "private_key_id": st.secrets["google_credentials"]["private_key_id"],
        "private_key": st.secrets["google_credentials"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["google_credentials"]["client_email"],
        "client_id": st.secrets["google_credentials"]["client_id"],
        "auth_uri": st.secrets["google_credentials"]["auth_uri"],
        "token_uri": st.secrets["google_credentials"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["google_credentials"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["google_credentials"]["client_x509_cert_url"],
        "universe_domain": st.secrets["google_credentials"]["universe_domain"]
    }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, ["https://www.googleapis.com/auth/spreadsheets"])

    gc = gspread.authorize(credentials)
    #gc = gspread.service_account.from_json_keyfile_name(filename="C:\\Users\\linco\\OneDrive\\Desktop\\Aescap\\Momentum\\stock-momentum-438620-d28ed2443e1a.json")
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1-cDCZDq8r1rGDVYpY_JhQvb0srhqsIiPhGWaxRC1TPw/edit?usp=sharing")
    previous = sh.sheet1.get('A2')
    future = sh.sheet1.get('B2')
          
    chats = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an artificial intelligence assistant, and your role is to "
                    f"present the latest news and updates along with the future news and update for {company_name} in a detailed, organized, and engaging manner."
            },
            {
                "role": "user",
                "content": f"Present the news and events aswell {company_name} over the past {time_period} retatining all the Dates aswell as the future news and events: Latest News and Updates text {previous}, Future News and Updates text {future}?"
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

def FUNDAMENTAL_ANALYSIS(file_name, company_name, file):

    temp_file_path = os.path.join(tempfile.gettempdir(), file)

# Write the contents to the temporary file
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_name.read())
    
    message_file = client.files.create(
    file=open(temp_file_path, "rb"), purpose="assistants"
    )

    file_id = message_file.id


    data = {"File_id": file_id, "Company Name": company_name, "File_name": file}

    webhook_url = "https://hook.eu2.make.com/d68cwl3ujkpqmgrnbpgy9mx3d06vs198"
    if webhook_url:
        response = requests.post(webhook_url,data)
    else: 
        print("Error")

    time.sleep(65)
    
    credentials_dict = {
        "type": st.secrets["google_credentials"]["type"],
        "project_id": st.secrets["google_credentials"]["project_id"],
        "private_key_id": st.secrets["google_credentials"]["private_key_id"],
        "private_key": st.secrets["google_credentials"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["google_credentials"]["client_email"],
        "client_id": st.secrets["google_credentials"]["client_id"],
        "auth_uri": st.secrets["google_credentials"]["auth_uri"],
        "token_uri": st.secrets["google_credentials"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["google_credentials"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["google_credentials"]["client_x509_cert_url"],
        "universe_domain": st.secrets["google_credentials"]["universe_domain"]
    }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, ["https://www.googleapis.com/auth/spreadsheets"])

    gc = gspread.authorize(credentials)
    #gc = gspread.service_account.from_json_keyfile_name(filename="C:\\Users\\linco\\OneDrive\\Desktop\\Aescap\\Momentum\\stock-momentum-438620-d28ed2443e1a.json")
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1-cDCZDq8r1rGDVYpY_JhQvb0srhqsIiPhGWaxRC1TPw/edit?usp=sharing")
    anaylsis = sh.sheet1.get('C2')

    chat_completion = client.chat.completions.create(
        model="gpt-4o",  # Ensure that you use a model available in your OpenAI subscription
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI model trained to format text for fundamental analysis of financial assets, with a focus on providing actionable recommendations. Your role is to structure content in a clear, logical, and standardized manner, organizing financial, operational, and strategic insights and concluding with practical recommendations. Your output should adhere to the following format:"
                    "Formatting Requirements:"
                    "Headings and Subheadings: Organize the analysis with concise, descriptive headings (e.g., “Financial Overview,” “Competitive Analysis,” “Investment Recommendations”)."
                    "Bullet Points and Numbered Lists: Use bullet points for concise lists of information and numbered lists for sequential steps or prioritized actions. This enhances readability, particularly in sections with extensive data."
                    "Consistent Formatting for Key Metrics:"
                    "Bold critical financial terms and ratios (e.g., Earnings Per Share (EPS), Price-to-Earnings Ratio (P/E))."
                    "Use italics for notable qualitative insights (e.g., industry trends, management stability)."
                    "Data Presentation: Where relevant, present numerical data in tables for easy comparison of metrics over time or against competitors. Include year-over-year changes to highlight trends in revenue, earnings, and key ratios."
                    "Structure Guidelines:"
                    "Introduction: Provide a concise overview of the asset, including industry context and the primary purpose of the analysis."
                    "Financial Analysis:"
                    "Income Statement: Summarize trends in revenue, cost of goods sold, operating income, and net income. Point out significant changes or growth patterns."
                    "Balance Sheet: Summarize assets, liabilities, and equity, focusing on liquidity and leverage metrics."
                    "Cash Flow Statement: Highlight cash flow from operating, investing, and financing activities, emphasizing cash generation capability and any unusual patterns."
                    "Key Ratios and Metrics:"
                    "Profitability Ratios (e.g., Gross Margin, Return on Assets)."
                    "Liquidity Ratios (e.g., Current Ratio, Quick Ratio)."
                    "Leverage Ratios (e.g., Debt-to-Equity Ratio)."
                    "Valuation Ratios (e.g., Price-to-Earnings Ratio, Price-to-Book Ratio)."
                    "Competitive Positioning and Market Analysis:"
                    "Provide an overview of the asset’s competitive position, market share, and primary competitors."
                    "Summarize industry trends and conduct a strengths, weaknesses, opportunities, and threats (SWOT) analysis to give context to the assets strategic position."
                    "Management and Governance:"
                    "Describe the executive team and board structure, noting experience, past performance, and any recent changes."
                    "Mention recent strategic decisions (e.g., acquisitions, new product lines) impacting performance."
                    "Conclusion and Outlook:"
                    "Offer a concise summary of the asset's strengths and potential risks based on financial and strategic positioning."
                    "Provide an outlook considering financial stability, industry conditions, and management’s strategic direction."
                    "Actionable Recommendations:"
                    "Investment Recommendation: Clearly state whether to Buy, Hold, or Sell the asset based on the findings. Justify this decision with reference to valuation metrics, market conditions, or management actions."
                    "Risk Management Suggestions: Outline potential risk mitigation strategies (e.g., sector diversification, stop-loss orders)."
                    "Strategic Suggestions for Management: If relevant, suggest strategic actions for the company itself, such as exploring new markets, reducing debt, or optimizing operational costs."
                    "Performance Monitoring Tips: Recommend specific metrics or events (e.g., quarterly earnings, regulatory updates) that investors should watch to evaluate ongoing asset performance."
                    "Style Requirements:"
                    "Maintain a professional, objective tone focused on analysis without personal opinions."
                    "Avoid excessive jargon, opting for straightforward explanations where necessary."
                    "Keep sentences and paragraphs clear and direct, ensuring the reader can easily follow your logic and conclusions."
                    "Following these guidelines will ensure that your output is professional, data-driven, and actionable, providing readers with clear insights and practical next steps for informed decision-making."
                    
                ),
            },
            {
                "role": "user",
                "content": (
                    f"fromat this text {anaylsis}"   
                ),
            },
        ]
    )

    # Extract and return the AI-generated response
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

def format_news(txt_summary):
    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # System message to define the assistant's behavior
            {
                "role": "system",
                "content":"You are an expert in formatting text for clarity and professional presentation. Your task is to prepare a well-organized, easy-to-read document summarizing recent events in font size 12 with attention to layout consistency. Follow these instructions:"
                "Text Formatting:"
                "Use font size 12 consistently across all text for readability."
                "Begin each entry with the Date and Event Title in bold to highlight key information upfront."
                "Event Description Structure:"
                "Organize each event entry in a structured format:"
                "Date: Bolded, immediately followed by the Event Title in bold on the same line."
                "Overview: Provide a concise summary of the event, outlining its main points."
                "Impact: Discuss potential implications or significance, especially regarding market"
                "Example Entry Format:"
                "[Date: October 15, 2024]"
                "[Event Title: Q3 Earnings Release]"
                "Overview: The company reported a strong year-over-year increase in Q3 revenue, primarily due to heightened demand in its core market."
                "Impact: Analysts predict this trend may lead to a stock price increase, as revenue growth outpaces industry averages."
                "Source: Company press release, MarketWatch article."

                
            },
            # User message with a prompt requesting stock analysis for a specific company
            {
                "role": "user",
                "content": f"text to format {txt_summary}"
                
            },
        ]
    )

# Output the AI's response
    response = chat_completion.choices[0].message.content
    return response


def update_progress(progress_bar, stage, progress, message):
    progress_bar.progress(progress)
    st.text(message)
    st.empty()

def plot_sma(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], mode='lines', name='SMA 20', line=dict(color='orange', dash='dash')))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], mode='lines', name='SMA 50', line=dict(color='red', dash='dash')))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_200'], mode='lines', name='SMA 200', line=dict(color='green', dash='dash')))
    return fig

# Function to plot Bollinger Bands
def plot_bbands(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['upper_band'], mode='lines', name='Upper Band', line=dict(color='cyan', dash='dot')))
    fig.add_trace(go.Scatter(x=data.index, y=data['middle_band'], mode='lines', name='Middle Band', line=dict(color='magenta', dash='dot')))
    fig.add_trace(go.Scatter(x=data.index, y=data['lower_band'], mode='lines', name='Lower Band', line=dict(color='cyan', dash='dot')))
    return fig

# Function to plot RSI
def plot_rsi(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='purple')))
    fig.add_hline(y=70, line=dict(color='red', dash='dash'))
    fig.add_hline(y=30, line=dict(color='green', dash='dash'))
    return fig

# Function to plot MACD
def plot_macd(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['MACD_signal'], mode='lines', name='MACD Signal', line=dict(color='red')))
    fig.add_trace(go.Bar(x=data.index, y=data['MACD_hist'], name='MACD Histogram', marker_color='gray', opacity=0.5))
    return fig

# Function to plot OBV
def plot_obv(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['OBV'], mode='lines', name='OBV', line=dict(color='brown')))
    return fig

# Function to plot ADX
def plot_adx(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['ADX'], mode='lines', name='ADX', line=dict(color='orange')))
    return fig


if __name__=="__main__":
    main()









