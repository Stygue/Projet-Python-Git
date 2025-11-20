import requests
import pandas as pd
import numpy as np
import datetime
from .caching import get_cached_crypto_data 

# Dictionnaire des IDs CoinGecko pour nos actifs
CRYPTO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana"
}

# La période d'historique que nous allons récupérer (par exemple, 1 an)
DAYS_HISTORY = 365 
CURRENCY = "usd"

def fetch_coingecko_data(asset_id: str, days: int = DAYS_HISTORY, currency: str = CURRENCY) -> pd.DataFrame:
    """
    Fetches historical price data for a single crypto asset from CoinGecko API.
    
    Args:
        asset_id (str): The CoinGecko ID of the asset (e.g., 'bitcoin').
        days (int): Number of days of history to fetch.
        currency (str): The currency for the price data (e.g., 'usd').
        
    Returns:
        pd.DataFrame: DataFrame with price data, indexed by date.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{asset_id}/market_chart?vs_currency={currency}&days={days}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Lève une exception si le statut HTTP est un échec
        data = response.json()
        
        if 'prices' not in data:
            print(f"Error: 'prices' not found for {asset_id}")
            return pd.DataFrame()

        # Convertir les données en DataFrame: [timestamp, price]
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        
        # Convertir le timestamp en datetime et le définir comme index
        # On utilise dt.date pour ne garder que la date, puis on le reconvertit en datetime index plus bas
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
        df = df.set_index('Date')['price'].rename(asset_id)
        
        return df.to_frame()

    except requests.exceptions.RequestException as e:
        # Gérer les erreurs (Robustness requirement)
        print(f"API request failed for {asset_id}: {e}")
        return pd.DataFrame()

def get_all_portfolio_data() -> pd.DataFrame:
    """
    Fetches and merges historical data for all portfolio assets (BTC, ETH, SOL).
    Uses the caching mechanism defined in caching.py.
    """
    all_data = []
    
    for symbol, cg_id in CRYPTO_IDS.items():
        # Utiliser la fonction de cache pour appeler la fonction de fetch
        df = get_cached_crypto_data(fetch_coingecko_data, asset_id=cg_id)
        
        if not df.empty:
            df.columns = [symbol] 
            all_data.append(df)
            
    if all_data:
        # Fusionner tous les DataFrames sur l'index 'Date'
        final_df = pd.concat(all_data, axis=1)
        final_df.index = pd.to_datetime(final_df.index)
        return final_df.dropna()
    else:
        return pd.DataFrame()