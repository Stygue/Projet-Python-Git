import streamlit as st
from data_handling.api_connector import CryptoDataFetcher
from typing import List

"""
This module handles data caching to optimize performance and reduce API calls.
It acts as a wrapper around the raw API connector.
"""

# Increase TTL (Time To Live) for historical data to 10 minutes (600 seconds)
# This prevents hitting API rate limits during frequent app usage.
@st.cache_data(ttl=600) 
def get_cached_historical_data(coin_id: str, days: str):
    """
    Wrapper to fetch historical data with Streamlit caching.
    Refreshes automatically every 10 minutes.
    """
    return CryptoDataFetcher.get_historical_data(coin_id, days)

@st.cache_data(ttl=60) # Cache data for 1 minute
def get_cached_current_price(coin_id: str):
    """
    Wrapper to fetch current price AND 24h change for a single asset (for Quant A).
    Returns (price, change_24h).
    """
    return CryptoDataFetcher.get_current_price(coin_id)

@st.cache_data(ttl=60) # Cache data for 1 minute
def get_cached_current_prices_batch(coin_ids: List[str]):
    """
    Wrapper to fetch current price AND 24h change for a batch of assets (for Home page).
    """
    return CryptoDataFetcher.get_current_prices_batch(coin_ids)
