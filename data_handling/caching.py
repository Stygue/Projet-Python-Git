import streamlit as st
import pandas as pd

# 5 minutes en secondes (5 * 60 = 300)
DATA_CACHE_TTL = 300 

@st.cache_data(ttl=DATA_CACHE_TTL)
def get_cached_crypto_data(fetch_function, *args, **kwargs) -> pd.DataFrame:
    """
    Cache wrapper for fetching crypto data.
    
    This function uses Streamlit's caching mechanism to store the data 
    and automatically re-run the underlying fetch_function only after 
    DATA_CACHE_TTL (5 minutes) has expired, meeting the project's requirement.
    
    Args:
        fetch_function: The function (e.g., from api_connector) that performs the API call.
        *args, **kwargs: Arguments passed to the fetch_function.
        
    Returns:
        pd.DataFrame: The fetched financial data.
    """
    try:
        data = fetch_function(*args, **kwargs)
        return data
    except Exception as e:
        st.error(f"Error fetching cached data: {e}")
        return pd.DataFrame()