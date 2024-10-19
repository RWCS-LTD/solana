import requests
import time
import pandas as pd
import streamlit as st

# Dune API keys and query details
api_key_1 = 'eFVEZrJ3PF7rYoT76upbQqcZkOdTmUbN'  # API key for token rankings query
api_key_2 = 'GWcsj2JQ9v4F6OgfuswS8tDmU8yMr2KX'  # API key for market signal query

query_id_1 = '4153109'  # Dune query ID for top-ranked tokens
query_id_2 = '4157858'  # Dune query ID for market signal

# Execute the query on Dune to get fresh data
def execute_query(query_id, api_key):
    url = f"https://api.dune.com/api/v1/query/{query_id}/execute"
    headers = {'x-dune-api-key': api_key}
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()['execution_id']
    else:
        st.error(f"Failed to execute query {query_id}: {response.status_code}")
        return None

# Check the status of the query execution
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

# Fetch the latest results after query execution is completed
def fetch_query_results(execution_id, api_key):
    url = f"https://api.dune.com/api/v1/execution/{execution_id}/results"
    headers = {'x-dune-api-key': api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch results for {execution_id}: {response.status_code}")
        return None

# Custom function to format the token ranking for visual appeal (Discord-like)
def display_token_rankings(token_df):
    st.subheader("🚀 **Top Ranked Tokens on Solana Blockchain**")
    for i, row in token_df.iterrows():
        token = row['token']
        score = row['final_score']
        rank = i + 1  # Adjusting rank to start from 1 instead of 0
        st.markdown(f"**{rank}.** 🏅 **{token}** — Score: **{score:.2f}**")

# Custom function to display market signal
def display_market_signal(signal, composite_score):
    st.subheader("📊 **Market Signal**")
    st.markdown(f"**Signal:** {signal} (Composite Score: **{composite_score:.2f}**)")

# Main function for the Streamlit app
def main():
    st.title("Solana Blockchain: Undervaluation vs Performance Rankings with Market Singal")

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

if __name__ == "__main__":
    main()
