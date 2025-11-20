import numpy as np
import pandas as pd
from scipy.stats import gmean

# Nous utilisons 365 pour les calculs d'annualisation pour les cryptos (24/7)
ANNUALIZATION_FACTOR = 365

def calculate_daily_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les rendements journaliers (logarithmiques) pour tous les actifs.
    """
    return np.log(price_df / price_df.shift(1)).dropna()

def simulate_portfolio(returns_df: pd.DataFrame, weights: list) -> pd.DataFrame:
    """
    Simule la performance cumulative du portefeuille basé sur des poids donnés.
    """
    # 1. Calculer les rendements du portefeuille (somme pondérée des rendements individuels)
    portfolio_returns = returns_df.dot(weights)
    
    # 2. Calculer la valeur cumulative (performance)
    # np.exp(returns.cumsum()) est la valeur cumulative d'un investissement de 1$
    cumulative_value = np.exp(portfolio_returns.cumsum())
    
    return pd.DataFrame({
        'Portfolio_Returns': portfolio_returns,
        'Cumulative_Value': cumulative_value
    })

def calculate_metrics(portfolio_returns: pd.Series, annualization_factor: int = ANNUALIZATION_FACTOR) -> dict:
    """
    Calcule les métriques de performance du portefeuille.
    """
    if portfolio_returns.empty:
        return {}
        
    # Rendement Annualisé
    annualized_return = portfolio_returns.mean() * annualization_factor

    # Volatilité Annualisée
    annualized_volatility = portfolio_returns.std() * np.sqrt(annualization_factor)

    # Ratio de Sharpe (Risk-Free Rate = 0 pour l'exemple)
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else 0

    # Max Drawdown
    # Utiliser les rendements arithmétiques pour le Drawdown
    cumulative = (1 + np.exp(portfolio_returns)).cumprod()
    peak = cumulative.expanding(min_periods=1).max()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()
    
    return {
        'Annualized Return': annualized_return,
        'Annualized Volatility': annualized_volatility,
        'Sharpe Ratio': sharpe_ratio,
        'Max Drawdown': max_drawdown
    }

def calculate_correlation(returns_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule la matrice de corrélation entre les rendements des actifs.
    """
    return returns_df.corr()