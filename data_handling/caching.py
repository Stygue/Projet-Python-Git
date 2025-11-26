import streamlit as st
from data_handling.api_connector import CryptoDataFetcher

"""
This module handles data caching to optimize performance and reduce API calls.
It acts as a wrapper around the raw API connector.
"""

@st.cache_data(ttl=300) # Cache data for 5 minutes (300 seconds)
def get_cached_historical_data(coin_id: str, days: str):
    """
    Wrapper to fetch historical data with Streamlit caching.
    Refreshes automatically every 5 minutes.
    """
    return CryptoDataFetcher.get_historical_data(coin_id, days)

@st.cache_data(ttl=60) # Cache data for 1 minute
def get_cached_current_price(coin_id: str):
    """
    Wrapper to fetch current price AND 24h change.
    Returns (price, change_24h).
    """
    return CryptoDataFetcher.get_current_price(coin_id)

