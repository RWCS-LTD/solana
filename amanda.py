import requests
import time
import pandas as pd
import streamlit as st

# Dune API keys and query details
api_key_1 = 'eFVEZrJ3PF7rYoT76upbQqcZkOdTmUbN'
api_key_2 = 'GWcsj2JQ9v4F6OgfuswS8tDmU8yMr2KX'

query_id_1 = '4153109'  # Token rankings query ID
query_id_2 = '4157858'  # Market signal query ID

# Function to execute query on Dune
def execute_query(query_id, api_key):
    url = f"https://api.dune.com/api/v1/query/{query_id}/execute"
    headers = {'x-dune-api-key': api_key}
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()['execution_id']
    else:
        st.error(f"Failed to execute query {query_id}: {response.status_code}")
        return None

# Function to check query status
def check_query_status(execution_id, api_key):
    url = f"https://api.dune.com/api/v1/execution/{execution_id}/status"
    headers = {'x-dune-api-key': api_key}
    while True:
        response = requests.get(url, headers=headers).json()
        if response['state'] == 'QUERY_STATE_COMPLETED':
            break
        elif response['state'] == 'QUERY_STATE_FAILED':
            st.error(f"Query {execution_id} failed.")
            return False
        time.sleep(30)
    return True

# Function to fetch query results
def fetch_query_results(execution_id, api_key):
    url = f"https://api.dune.com/api/v1/execution/{execution_id}/results"
    headers = {'x-dune-api-key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch results for {execution_id}: {response.status_code}")
        return None

# Function to display token rankings
def display_token_rankings(token_df):
    st.subheader("🚀 **Top Ranked Tokens on Solana Blockchain**")
    for i, row in token_df.iterrows():
        token = row['token']
        score = row['final_score']
        rank = i + 1  # Adjusting rank to start from 1 instead of 0
        st.markdown(f"**{rank}.** 🏅 **{token}** — Score: **{score:.2f}**")

# Function to display market signal
def display_market_signal(signal, composite_score):
    st.subheader("📊 **Market Signal**")
    st.markdown(f"**Signal:** {signal} (Composite Score: **{composite_score:.2f}**)")

# Main function for Streamlit app
def main():
    st.title("Solana Blockchain: Undervaluation vs Performance Rankings with Market Signal")

    # Add button to fetch and visualize data
    if st.button("Run Analysis"):
        st.write("Executing program...")

        # Execute and retrieve token rankings
        token_execution_id = execute_query(query_id_1, api_key_1)
        if not token_execution_id:
            return

        # Execute and retrieve market signal
        market_signal_execution_id = execute_query(query_id_2, api_key_2)
        if not market_signal_execution_id:
            return

        # Wait for both queries to finish
        st.write("Waiting for queries to complete...")
        if not check_query_status(token_execution_id, api_key_1):
            return
        if not check_query_status(market_signal_execution_id, api_key_2):
            return

        # Fetch the results of both queries
        token_results = fetch_query_results(token_execution_id, api_key_1)
        market_signal_results = fetch_query_results(market_signal_execution_id, api_key_2)

        if not token_results or not market_signal_results:
            st.error("Failed to fetch results from one or both queries.")
            return

        # Parse and display market signal data
        signal_row = market_signal_results['result']['rows'][0]
        composite_score = round(signal_row['composite_score'], 2)
        signal = signal_row['signal']

        # Display Market Signal
        display_market_signal(signal, composite_score)

        # Parse and display token rankings
        token_df = pd.DataFrame(token_results['result']['rows'])
        display_token_rankings(token_df)

    # Detailed explanation sections
    st.header("Understanding the Market Signal and Token Ranking Process")

    # Explanation for Market Signal
    with st.expander("🔍 How the Market Signal is Generated"):
        st.markdown("""
        ### Explanation of the Composite Score for Market Signal
        The **composite score** is a combined metric that gives an overall view of market conditions based on 
        three important factors: **volume trend**, **price momentum**, and **network activity**. By evaluating 
        these three components together, traders can get a clearer sense of market direction and make more informed 
        trading decisions.

        1. **Volume Trend (VT Score)**:
           - **What It Is**: This metric looks at the total trading volume (in USD) on the Solana blockchain over 
             the past day and compares it to the average volume over the past 3 days.
           - **How It Works**:
               - If today’s trading volume is **higher** than the 3-day average, the volume trend score 
                 (`vt_score`) will be +1.
               - If today’s trading volume is **lower**, the score will be -1.
           - **Why It Matters**: Rising volume can indicate increasing market interest and potential price movements, 
             while declining volume may signal weakening interest or indecisiveness.

        2. **Price Momentum (PM Score)**:
           - **What It Is**: This metric measures the **day-to-day price movement** of key tokens on the Solana blockchain. 
             It calculates whether prices have gone up or down compared to the previous day.
           - **How It Works**:
               - If the price today is **higher** than yesterday’s, the price momentum score (`pm_score`) will be +1.
               - If the price is **lower**, the score will be -1.
           - **Why It Matters**: Positive price momentum suggests that the market may be bullish, while negative 
             momentum can indicate bearish conditions or potential sell-offs.

        3. **Network Activity (NA Score)**:
           - **What It Is**: This metric looks at the **number of transactions** happening on the Solana blockchain today 
             and compares it to the average transaction count over the past 3 days.
           - **How It Works**:
               - If today’s transaction count is **higher** than the 3-day average, the network activity score (`na_score`) 
                 will be +1.
               - If the transaction count is **lower**, the score will be -1.
           - **Why It Matters**: Higher network activity suggests increased usage of the blockchain (e.g., more people 
             trading or interacting with decentralized apps), which can be a bullish signal. Lower activity may suggest 
             stagnation or reduced market interest.

        ### Composite Score and Market Signal:
        - The **composite score** is calculated by summing the individual scores from the three metrics:
            - VT Score (volume trend)
            - PM Score (price momentum)
            - NA Score (network activity)
        - The final **composite score** will range between +3 (all metrics are positive) to -3 (all metrics are negative).

        **How to Interpret the Composite Score**:
        - **Positive Composite Score (> 0)**: Indicates that the market conditions are bullish, and the signal will be 
          “**Long**,” meaning it may be a good time to consider buying or holding positions.
        - **Negative Composite Score (<= 0)**: Indicates bearish or uncertain conditions, and the signal will be 
          “**Hold Cash**,” implying it may be safer to stay out of the market.

        ### Example Interpretation:
        - **Composite Score = -2.05, Signal = "Hold Cash"**:
          - This suggests that the market is showing weak volume, declining prices, and/or low transaction activity.
          - The "Hold Cash" signal suggests caution and recommends holding cash or avoiding new trades until the market 
            shows signs of improvement.
        """)

    # Explanation for Token Ranking
    with st.expander("📊 How the Tokens Are Ranked"):
        st.markdown("""
        ### How Are the Tokens Ranked?
        We use a systematic approach to rank tokens based on their **trading activity** and **market cap proxy** 
        (calculated as total volume multiplied by price) over the last 24 hours. Here’s how it works:

        1. **Categorizing Tokens by Market Cap Proxy and Trading Volume**:
           - Tokens are classified into three categories based on their total trading volume and market cap proxy 
             over the last 24 hours:
               - **Small-Cap/High-Volume Tokens**: Market cap less than $5 million$, trading volume greater than $1 million$.
               - **Mid-Cap/Moderate-Volume Tokens**: Market cap between $5 million$ and $100 million$.
               - **Large-Cap/High-Volume Tokens**: Market cap above $100 million$.

        2. **Combining the Categories**:
           - After categorizing tokens into these three groups, we combine them into a single list. This ensures that both 
             large and smaller tokens with significant trading activity are considered for final ranking.

        3. **Selecting the Top Tokens**:
           - From this combined list, we select the **top 10 tokens** based on their total trading volume in the last 
             24 hours. These tokens are ranked based on how active they are in the market, with a focus on those showing 
             high interest and activity.

        ### How Does the Scoring System Work?
        - In addition to categorizing tokens based on market cap and volume, we use a **scoring system** that ranks 
          the tokens based on key metrics:

        #### 1. **Price-Volume Ratio (PVR)**
           - **What It Is**: The Price-Volume Ratio compares how much a token is traded (volume) relative to its price.
           - **How It Affects the Score**: If the token’s PVR is **lower** than the average, it receives a +1 score. This indicates that the token might be undervalued relative to how much it’s being traded.
           - **Why It Matters**: A lower PVR can suggest that the token is trading at a higher volume than its price would indicate, which might signal an opportunity for investors.

        #### 2. **Relative Volume (RVOL)**
           - **What It Is**: This metric compares how much a token was traded in the last 24 hours compared to its average volume over the past 7 days.
           - **How It Affects the Score**: If the token’s 24-hour volume is **higher** than the 7-day average, it gets a +1 score, indicating strong market interest. If the 24-hour volume is **lower**, it receives a -1 score.
           - **Why It Matters**: Higher RVOL suggests growing market interest in the token, which can indicate momentum and future price growth. Lower RVOL might show waning interest.

        #### 3. **Momentum**
           - **What It Is**: This metric measures the price change of the token over the past 3 days.
           - **How It Affects the Score**: If the token’s price is **rising** over the past 3 days, it gets a +1 score. If the price is **decreasing**, it gets a -1 score.
           - **Why It Matters**: Momentum is a key indicator of whether a token is gaining or losing favor in the market. A positive momentum score indicates bullish sentiment, while a negative score signals a bearish trend.

        #### 4. **PVR Deviation (PVRD)**
           - **What It Is**: PVR Deviation compares the token’s PVR to the average PVR.
           - **How It Affects the Score**: If the token’s PVRD is **negative** (lower than the average), it gets a +1 score. This could indicate that the token is undervalued compared to how much it’s being traded.
           - **Why It Matters**: PVRD highlights tokens that are potentially undervalued based on the relationship between their trading volume and price.

        #### 5. **Volume Score Index (VSI)**
           - **What It Is**: The Volume Score Index measures how much the token has been traded in the last 24 hours relative to its historical average volume.
           - **How It Affects the Score**: If the token’s VSI is **higher** than average, it gets a +1 score. This indicates that the token is attracting more attention than normal, which might suggest bullish sentiment.
           - **Why It Matters**: A high VSI suggests that the token is seeing significantly more trading activity, which could lead to price increases.

        ### How to Interpret the Final Score:
        - Each token receives a score based on these five metrics, with the final score determining its rank.
        - A **+5 score** means the token is excelling across all metrics (PVR, RVOL, Momentum, PVRD, and VSI).
        - A **negative score** (closer to -5) indicates the token is underperforming on most of these metrics, suggesting it might not be the best choice at the moment.
        """)

if __name__ == "__main__":
    main()

