import requests
import pandas as pd
from typing import Optional, Tuple, List, Dict
import time

class CryptoDataFetcher:
    """
    Handles data retrieval from CoinGecko API.
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3"

    @staticmethod
    def get_historical_data(coin_id: str, days: str = "30") -> Optional[pd.DataFrame]:
        """
        Fetches historical market data (price vs timestamp) for a specific asset.
        """
        url = f"{CryptoDataFetcher.BASE_URL}/coins/{coin_id}/market_chart"
        
        params = {
            "vs_currency": "usd",
            "days": days
        }
        
        # Optimization: Use 'daily' interval for long durations to reduce data size
        if days.isdigit() and int(days) > 90:
            params['interval'] = 'daily'

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            # Handle Rate Limiting (CoinGecko free tier limitation)
            if response.status_code == 429:
                print(f"⚠️ API ERROR (429): Rate Limit Exceeded for {coin_id}. Waiting 10 seconds before returning None.")
                time.sleep(10) 
                return None
            
            if response.status_code != 200:
                print(f"⚠️ API ERROR ({response.status_code}): {response.text}")
                return None
            
            data = response.json()
            
            if 'prices' not in data:
                print(f"⚠️ No 'prices' data received for {coin_id}")
                return None

            # Convert to DataFrame and process timestamps
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df

        except Exception as e:
            print(f"❌ Technical Exception: {e}")
            return None

    @staticmethod
    def get_current_price(coin_id: str) -> Tuple[float, float]:
        """
        Fetches current price AND 24h change for a single asset.
        Used primarily for the Single Asset module (Quant A).
        """
        url = f"{CryptoDataFetcher.BASE_URL}/simple/price"
        params = {
            "ids": coin_id, 
            "vs_currencies": "usd",
            "include_24hr_change": "true" 
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 429:
                print(f"⚠️ API ERROR (429) for current price {coin_id}. Returning 0.0, 0.0.")
                return 0.0, 0.0
            
            if response.status_code == 200:
                data = response.json()
                coin_data = data.get(coin_id, {})
                price = coin_data.get('usd', 0.0)
                change = coin_data.get('usd_24h_change', 0.0)
                return price, change
        except Exception:
            return 0.0, 0.0
        return 0.0, 0.0

    @staticmethod
    def get_current_prices_batch(coin_ids: List[str]) -> Dict[str, Tuple[float, float]]:
        """
        Fetches current prices for multiple assets in a single request.
        Optimized to save API calls.
        Returns: {'bitcoin': (price, 24h_change), ...}
        """
        if not coin_ids:
            return {}
            
        url = f"{CryptoDataFetcher.BASE_URL}/simple/price"
        params = {
            "ids": ",".join(coin_ids), 
            "vs_currencies": "usd",
            "include_24hr_change": "true" 
        }
        
        results = {}
        
        try:
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 429:
                print(f"⚠️ API ERROR (429) for price batch. Returning empty data.")
                return {}

            if response.status_code == 200:
                data = response.json()
                for coin_id in coin_ids:
                    coin_data = data.get(coin_id, {})
                    price = coin_data.get('usd', 0.0)
                    change = coin_data.get('usd_24h_change', 0.0)
                    results[coin_id] = (price, change)
        except Exception as e:
            print(f"❌ Technical Exception during batch price fetch: {e}")
            return {}
            
        return results
