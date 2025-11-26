import requests
import pandas as pd
from typing import Optional

class CryptoDataFetcher:
    """
    Handles data retrieval from CoinGecko API.
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3"

    @staticmethod
    def get_historical_data(coin_id: str, days: str = "30") -> Optional[pd.DataFrame]:
        url = f"{CryptoDataFetcher.BASE_URL}/coins/{coin_id}/market_chart"
        
        # --- CORRECTION ---
        # On ne demande plus "hourly" explicitement car c'est réservé aux comptes payants.
        # On laisse CoinGecko décider de la précision (automatique).
        params = {
            "vs_currency": "usd",
            "days": days
        }
        
        # On ajoute 'daily' seulement si on demande plus de 90 jours pour alléger la réponse
        if days.isdigit() and int(days) > 90:
            params['interval'] = 'daily'

        # Headers pour éviter d'être bloqué (User-Agent)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"⚠️ ERREUR API ({response.status_code}): {response.text}")
                return None
            
            data = response.json()
            
            if 'prices' not in data:
                print(f"⚠️ Pas de données 'prices' reçues pour {coin_id}")
                return None

            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df

        except Exception as e:
            print(f"❌ Exception technique : {e}")
            return None

    @staticmethod
    def get_current_price(coin_id: str) -> tuple:
        """
        Récupère le prix actuel ET la variation 24h.
        Retourne un tuple : (prix, variation_24h)
        """
        url = f"{CryptoDataFetcher.BASE_URL}/simple/price"
        # On ajoute 'include_24hr_change' à true
        params = {
            "ids": coin_id, 
            "vs_currencies": "usd",
            "include_24hr_change": "true" 
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                coin_data = data.get(coin_id, {})
                price = coin_data.get('usd', 0.0)
                change = coin_data.get('usd_24h_change', 0.0)
                return price, change
        except Exception:
            return 0.0, 0.0
        return 0.0, 0.0

