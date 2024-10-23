import requests
import time
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# Dune API keys and query details
api_key_1 = 'eFVEZrJ3PF7rYoT76upbQqcZkOdTmUbN'
api_key_2 = 'GWcsj2JQ9v4F6OgfuswS8tDmU8yMr2KX'
api_key_3 = 'geV9mpnqYUeSZzz1crWBRQ3HpRbv9SmD'

query_id_1 = '4153109'  # Token rankings query ID
query_id_2 = '4157858'  # Market signal query ID
query_id_3 = '4158056'  # Hourly returns for SOL query ID

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

# Function to display heatmap for hourly returns
def display_heatmap(hourly_return_df):
    st.subheader("📈 **Hourly Returns Heatmap (SOL)**")
    
    # Define the correct order for days of the week
    day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    # Convert the day_name column to a categorical type with the specified order
    hourly_return_df['day_name'] = pd.Categorical(hourly_return_df['day_name'], categories=day_order, ordered=True)
    
    # Use pivot to reshape the DataFrame for the heatmap
    pivot_df = hourly_return_df.pivot(index="hour_of_day", columns="day_name", values="avg_hourly_return")
    
    # Plotting the heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_df, annot=True, cmap="coolwarm", ax=ax)
    ax.set_title('Average Hourly Return by Day of Week and Hour of Day')
    st.pyplot(fig)

def display_line_chart(hourly_return_df):
    st.subheader("📊 **Average Hourly Returns by Day**")
    
    # Use line plot to show hourly returns for each day
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=hourly_return_df, x="hour_of_day", y="avg_hourly_return", hue="day_name", marker="o")
    
    # Add labels and title
    plt.title('Average Hourly Return by Day of Week and Hour of Day')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Hourly Return')
    plt.grid(True)
    st.pyplot(plt)

def display_boxplot(hourly_return_df):
    st.subheader("📊 **Distribution of Hourly Returns by Day**")
    
    # Plotting the box plot to display distribution of returns by day
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=hourly_return_df, x="day_name", y="avg_hourly_return", hue="day_name", palette="Set2", dodge=False)
    
    # Add labels and title
    plt.title('Hourly Return Distribution by Day of Week')
    plt.xlabel('Day of Week')
    plt.ylabel('Hourly Return')
    plt.grid(True)
    st.pyplot(plt)

def display_bar_chart(hourly_return_df):
    st.subheader("📊 **Total Average Returns by Day**")
    
    # Calculate total average return per day, adding observed=True to suppress the warning
    total_returns_df = hourly_return_df.groupby('day_name', observed=True)['avg_hourly_return'].sum().reset_index()
    
    # Plotting bar chart
    plt.figure(figsize=(10, 6))
    sns.barplot(data=total_returns_df, x="day_name", y="avg_hourly_return", hue="day_name", palette="muted", dodge=False)
    
    # Add labels and title
    plt.title('Total Average Hourly Return by Day of Week')
    plt.xlabel('Day of Week')
    plt.ylabel('Total Average Return')
    st.pyplot(plt)

def display_filtered_heatmap(hourly_return_df, threshold=0.3):
    st.subheader("📊 **Heatmap of High-Return Hours (Threshold: +/- {:.2f})**".format(threshold))
    
    # Filter the DataFrame to show only returns greater than or less than the threshold
    filtered_df = hourly_return_df[(hourly_return_df['avg_hourly_return'] > threshold) | (hourly_return_df['avg_hourly_return'] < -threshold)]
    
    # Use pivot to reshape the DataFrame for heatmap
    pivot_df = filtered_df.pivot(index="hour_of_day", columns="day_name", values="avg_hourly_return")
    
    # Plotting the heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_df, annot=True, cmap="coolwarm", ax=ax, vmin=-1, vmax=1)
    ax.set_title('High-Return Hours by Day of Week and Hour of Day')
    st.pyplot(fig)

def display_rolling_average(hourly_return_df, window=3):
    st.subheader(f"📊 **Rolling Average of Hourly Returns (Window: {window} hours)**")
    
    # Calculate the rolling average of the hourly returns
    hourly_return_df['rolling_avg'] = hourly_return_df.groupby('day_name', observed=True)['avg_hourly_return'].transform(lambda x: x.rolling(window).mean())
    
    # Use line plot to show rolling average
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=hourly_return_df, x="hour_of_day", y="rolling_avg", hue="day_name", marker="o")
    
    # Add labels and title
    plt.title(f'Rolling Average Hourly Return by Day of Week (Window: {window} hours)')
    plt.xlabel('Hour of Day')
    plt.ylabel('Rolling Average Hourly Return')
    plt.grid(True)
    st.pyplot(plt)

# Main function for Streamlit app
def main():
    st.title("Solana Blockchain: Undervaluation vs Performance Rankings; with Market Signal and Hourly Average Returns for SOL")

    # Button to run Market Signal and Token Rankings queries
    if st.button("Run Market Signal and Token Rankings Analysis"):
        st.write("Executing Market Signal and Token Rankings...")

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

    # Button to run SOL Hourly Returns query
    if st.button("Run SOL Hourly Returns Analysis"):
        st.write("Executing SOL Hourly Returns Analysis...")

        # Execute and retrieve third query (hourly returns for SOL)
        sol_return_execution_id = execute_query(query_id_3, api_key_3)
        if not sol_return_execution_id:
            return

        # Wait for query to finish
        st.write("Waiting for query to complete...")
        if not check_query_status(sol_return_execution_id, api_key_3):
            return

        # Fetch the results of the query
        sol_return_results = fetch_query_results(sol_return_execution_id, api_key_3)
        if not sol_return_results:
            st.error("Failed to fetch results for SOL Hourly Returns.")
            return

        # Parse and display heatmap for hourly returns
        hourly_return_df = pd.DataFrame(sol_return_results['result']['rows'])
        display_heatmap(hourly_return_df)

        # Additional Visualizations
        display_line_chart(hourly_return_df)   # Line chart by hour
        display_boxplot(hourly_return_df)      # Box plot by day
        display_bar_chart(hourly_return_df)    # Bar chart for total returns
        display_rolling_average(hourly_return_df, window=3)  # Rolling average with a 3-hour window

        # Optional: Filtered heatmap (with threshold of 0.05, adjust as needed)
        display_filtered_heatmap(hourly_return_df, threshold=0.3)

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

    # Explanation for SOL hourly returns visualizations
    with st.expander("🌍 How the SOL Hourly Returns are Visualized"):
        st.markdown("""
        ### How the Hourly Returns for SOL are Calculated and Visualized
        This analysis computes the **average hourly returns** for the SOL token on the Solana blockchain, offering multiple visualizations to uncover deeper insights. Here's how the data is processed and visualized:

        #### 1. **Data Source**:
        - The hourly price of SOL is sourced from the DEX Solana data over the past 3 months.

        #### 2. **Timezone Adjustment**:
        - The data is adjusted to the **Toronto timezone (UTC-4)** to better reflect North American trading patterns.

        #### 3. **Return Calculation**:
        - The hourly return is computed as the percentage change from one hour to the next.

        #### 4. **Heatmap**: 
        - The **average hourly returns** are grouped by **day of the week** and **hour of the day** to create a heatmap. This allows users to quickly identify specific hours and days when SOL's price shows significant patterns or trends, such as periods of high volatility or stability.

        #### 5. **Line Chart**: 
        - A **line chart** is provided to show the trend of hourly returns throughout the day for each day of the week. This helps to highlight patterns across the days and visualize how returns fluctuate hour by hour.

        #### 6. **Box Plot**: 
        - The **box plot** displays the distribution of hourly returns for each day of the week, showing the variability (spread) of returns, as well as potential outliers. This allows users to see which days are more volatile or consistent in terms of returns.

        #### 7. **Bar Chart**:
        - The **bar chart** shows the **total average returns** for each day of the week, helping users to quickly identify which days tend to be more profitable or less profitable over the observed period.

        #### 8. **Filtered Heatmap**: 
        - A **filtered heatmap** highlights only the hours with significant positive or negative returns, based on a predefined threshold. This is useful for focusing attention on high-return or high-risk trading periods.

        #### 9. **Rolling Average Line Plot**:
        - The **rolling average line plot** smooths out hourly return fluctuations over a chosen window (e.g., 3 hours), allowing users to observe overall trends while reducing noise. This is helpful for spotting broader market cycles or shifts in trading momentum.

        These visualizations together provide a comprehensive view of how SOL's price movements vary by time, helping users make more informed trading decisions based on historical performance and patterns.
        """)

if __name__ == "__main__":
    main()
