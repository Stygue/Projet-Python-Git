import pandas as pd
import numpy as np

def get_performance_summary(df: pd.DataFrame, col_name: str = 'price'):
    """
    Calcule les métriques en gérant intelligemment PRIX ou RENDEMENTS.
    """
    # 1. Sécurité de base
    if df is None or df.empty:
        return _empty_metrics()

    df = df.copy()
    df = df.sort_index() # Toujours trier par date

    # --- DÉTECTION INTELLIGENTE ---
    # Si la colonne s'appelle 'returns' ou qu'on ne trouve pas de 'price'
    is_returns_data = (col_name == 'returns') or ('price' not in df.columns and 'returns' in df.columns)

    if is_returns_data:
        # CAS A : On a reçu des pourcentages (Ton cas actuel)
        # On s'assure que la colonne 'returns' existe
        target_col = 'returns' if 'returns' in df.columns else col_name
        
        # On nettoie les données
        df['returns'] = pd.to_numeric(df[target_col], errors='coerce').fillna(0)
        
        # ON RECONSTRUIT UN PRIX ARTIFICIEL (Base 100)
        # Cela permet de calculer le Drawdown et le Total Return correctement
        df['synthetic_price'] = (1 + df['returns']).cumprod() * 100
        price_col = 'synthetic_price'
        
    else:
        # CAS B : On a reçu des vrais prix (Cas classique)
        price_col = col_name if col_name in df.columns else df.columns[0]
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
        df = df.dropna(subset=[price_col])
        
        # On calcule les rendements
        df['returns'] = df[price_col].pct_change().fillna(0)

    # --- CALCULS ---
    
    # 1. Rendement Total
    # On utilise le prix (réel ou synthétique)
    if len(df) > 0:
        start_price = df[price_col].iloc[0]
        end_price = df[price_col].iloc[-1]
        if start_price == 0:
            total_return = 0.0
        else:
            total_return = (end_price - start_price) / start_price
    else:
        total_return = 0.0

    # 2. Volatilité Annualisée
    # On utilise les rendements
    volatility = df['returns'].std() * np.sqrt(365)

    # 3. Sharpe Ratio
    avg_annual_return = df['returns'].mean() * 365
    if volatility == 0 or pd.isna(volatility):
        sharpe_ratio = 0.0
    else:
        sharpe_ratio = avg_annual_return / volatility

    # 4. Max Drawdown
    # On utilise le prix (réel ou synthétique) pour voir la chute du sommet au creux
    rolling_max = df[price_col].cummax()
    drawdown = (df[price_col] - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # Nettoyage final des résultats
    return {
        "Total Return": 0.0 if pd.isna(total_return) else total_return,
        "Volatility": 0.0 if pd.isna(volatility) else volatility,
        "Sharpe Ratio": 0.0 if pd.isna(sharpe_ratio) else sharpe_ratio,
        "Max Drawdown": 0.0 if pd.isna(max_drawdown) else max_drawdown
    }

def _empty_metrics():
    return {
        "Total Return": 0.0,
        "Volatility": 0.0,
        "Sharpe Ratio": 0.0,
        "Max Drawdown": 0.0
    }
