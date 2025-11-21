import requests
import pandas as pd
import time
from typing import Optional

class CryptoDataFetcher:
    """
    Handles data retrieval from CoinGecko API.
    Designed to be robust and handle API errors gracefully.
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3"

    @staticmethod
    def get_historical_data(coin_id: str, days: str = "30") -> Optional[pd.DataFrame]:
        """
        Fetches historical market data (prices) for a specific coin.
        
        Args:
            coin_id (str): The ID of the coin (e.g., 'bitcoin', 'ethereum', 'solana').
            days (str): Data range in days (e.g., '1', '14', '30', 'max').
            
        Returns:
            pd.DataFrame: DataFrame with 'timestamp' and 'price' columns, or None if error.
        """
        url = f"{CryptoDataFetcher.BASE_URL}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": "daily" if int(days) > 90 else "hourly" # Adjust granularity
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status() # Raise error for bad status codes (4xx, 5xx)
            
            data = response.json()
            
            if 'prices' not in data:
                print(f"Error: No price data found for {coin_id}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            
            # Convert timestamp (ms) to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df

        except requests.exceptions.RequestException as e:
            print(f"API Request Error for {coin_id}: {e}")
            return None
        except ValueError as e:
            print(f"Data Parsing Error: {e}")
            return None

    @staticmethod
    def get_current_price(coin_id: str) -> float:
        """
        Fetches the real-time price of a coin.
        """
        url = f"{CryptoDataFetcher.BASE_URL}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd"
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get(coin_id, {}).get('usd', 0.0)
        except Exception as e:
            print(f"Error fetching current price for {coin_id}: {e}")
            return 0.0
