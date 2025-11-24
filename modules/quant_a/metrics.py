import pandas as pd
import numpy as np

def get_performance_summary(df: pd.DataFrame, col_name: str = 'price'):
    """
    Calcule les métriques avec protection totale contre les divisions par zéro et les infinis.
    """
    # 1. Sécurité de base
    if df is None or df.empty:
        return _empty_metrics()

    df = df.copy()
    df = df.sort_index()

    # --- DÉTECTION ET NORMALISATION ---
    # On détermine si on travaille sur des PRIX ou des RENDEMENTS
    is_returns_data = (col_name == 'returns') or ('price' not in df.columns and 'returns' in df.columns)

    if is_returns_data:
        # Cas : Pourcentages (Returns)
        target_col = 'returns' if 'returns' in df.columns else col_name
        
        # Nettoyage agressif des rendements
        # On remplace les infinis par NaN, puis les NaN par 0
        df['returns'] = pd.to_numeric(df[target_col], errors='coerce')
        df['returns'] = df['returns'].replace([np.inf, -np.inf], np.nan).fillna(0)
        
        # Construction du Prix Synthétique (Base 100)
        # On ajoute 1e-9 pour éviter d'avoir un prix strictement égal à 0
        df['price_metrics'] = (1 + df['returns']).cumprod() * 100
        
    else:
        # Cas : Prix réels
        target_col = col_name if col_name in df.columns else df.columns[0]
        df['price_metrics'] = pd.to_numeric(df[target_col], errors='coerce')
        df = df.dropna(subset=['price_metrics'])
        
        # Calcul des rendements
        df['returns'] = df['price_metrics'].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)

    # Si après nettoyage on a moins de 2 lignes, on arrête
    if len(df) < 2:
        return _empty_metrics()

    # --- CALCULS ---

    # 1. Rendement Total
    start_price = df['price_metrics'].iloc[0]
    end_price = df['price_metrics'].iloc[-1]
    
    if start_price <= 0: # Protection division
        total_return = 0.0
    else:
        total_return = (end_price - start_price) / start_price

    # 2. Volatilité
    volatility = df['returns'].std() * np.sqrt(365)

    # 3. Sharpe Ratio
    avg_annual_return = df['returns'].mean() * 365
    if volatility == 0 or pd.isna(volatility):
        sharpe_ratio = 0.0
    else:
        sharpe_ratio = avg_annual_return / volatility

    # 4. Max Drawdown (Le point critique)
    rolling_max = df['price_metrics'].cummax()
    
    # On remplace les 0 dans rolling_max par une toute petite valeur pour éviter la division par zéro
    rolling_max = rolling_max.replace(0, 1e-9)
    
    drawdown = (df['price_metrics'] - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # --- NETTOYAGE FINAL DES RÉSULTATS ---
    # On s'assure qu'aucun résultat n'est infini ou NaN
    def clean_val(val):
        if pd.isna(val) or np.isinf(val):
            return 0.0
        return val

    return {
        "Total Return": clean_val(total_return),
        "Volatility": clean_val(volatility),
        "Sharpe Ratio": clean_val(sharpe_ratio),
        "Max Drawdown": clean_val(max_drawdown)
    }

def _empty_metrics():
    return {
        "Total Return": 0.0,
        "Volatility": 0.0,
        "Sharpe Ratio": 0.0,
        "Max Drawdown": 0.0
    }
