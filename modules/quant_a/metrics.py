import pandas as pd
import numpy as np

def get_performance_summary(df: pd.DataFrame, col_name: str = 'price'):
    """
    Calcule les métriques clés.
    """
    # Sécurité : si le tableau est vide
    if df is None or df.empty:
        return {
            "Total Return": 0.0,
            "Volatility": 0.0,
            "Sharpe Ratio": 0.0,
            "Max Drawdown": 0.0
        }
    
    # Gestion de la colonne
    if col_name not in df.columns:
        col_name = 'price' if 'price' in df.columns else df.columns[0]

    df = df.copy()
    
    # Calcul des rendements
    df['returns'] = df[col_name].pct_change()

    # 1. Rendement Total
    start_price = df[col_name].iloc[0]
    end_price = df[col_name].iloc[-1]
    total_return = (end_price - start_price) / start_price

    # 2. Volatilité Annualisée
    volatility = df['returns'].std() * np.sqrt(365)

    # 3. Sharpe Ratio
    avg_annual_return = df['returns'].mean() * 365
    if volatility == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = avg_annual_return / volatility

    # 4. Max Drawdown
    rolling_max = df[col_name].cummax()
    drawdown = (df[col_name] - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # --- CORRECTION DES NOMS ICI ---
    # On renvoie exactement les noms que ui.py attend
    return {
        "Total Return": total_return,  
        "Volatility": volatility,      
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown
    }
