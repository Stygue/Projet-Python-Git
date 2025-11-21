import pandas as pd
import numpy as np

def get_performance_summary(df: pd.DataFrame):
    """
    Calcule les métriques clés : Rendement, Volatilité, Sharpe, Drawdown.
    Prend en entrée le DataFrame nettoyé par api_connector.
    """
    # Sécurité : si le tableau est vide
    if df is None or df.empty:
        return {
            "Total Return": 0.0,
            "Annual Volatility": 0.0,
            "Sharpe Ratio": 0.0,
            "Max Drawdown": 0.0
        }

    # On s'assure d'avoir les rendements journaliers
    # La colonne 'price' vient de ton api_connector
    df = df.copy() # Pour ne pas modifier l'original
    df['returns'] = df['price'].pct_change()

    # 1. Rendement Total (Fin - Début) / Début
    start_price = df['price'].iloc[0]
    end_price = df['price'].iloc[-1]
    total_return = (end_price - start_price) / start_price

    # 2. Volatilité Annualisée (Crypto = 365 jours de trading)
    volatility = df['returns'].std() * np.sqrt(365)

    # 3. Sharpe Ratio (Rentabilité / Risque)
    # On annualise le rendement moyen
    avg_annual_return = df['returns'].mean() * 365
    if volatility == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = avg_annual_return / volatility

    # 4. Max Drawdown (La pire chute depuis un sommet)
    rolling_max = df['price'].cummax()
    drawdown = (df['price'] - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    return {
        "Total Return": total_return,
        "Annual Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown
    }
