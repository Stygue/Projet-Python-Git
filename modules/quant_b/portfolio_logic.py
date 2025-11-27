import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from data_handling.caching import get_cached_historical_data

# --- CONSTANTS ---
# Dictionary mapping display names to CoinGecko IDs
SUPPORTED_ASSETS = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Solana": "solana",
    "Cardano": "cardano",
    "Polkadot": "polkadot"
}

# --- PRIMARY FUNCTION: DATA LOADING ---
def load_multi_asset_data(asset_ids: List[str], days: str = "365") -> Optional[pd.DataFrame]:
    """
    Loads historical price data for a list of assets, synchronizing and cleaning the time series.
    
    Args:
        asset_ids (List[str]): The CoinGecko IDs of the cryptocurrencies.
        days (str): The historical period to retrieve (e.g., '365').
        
    Returns:
        Optional[pd.DataFrame]: DataFrame with one price column per asset, or None if failed.
    """
    all_prices = {}
    
    # Fetch data for each selected asset using the common caching mechanism
    for asset_id in asset_ids:
        # Use common cached function to reduce API load
        df = get_cached_historical_data(asset_id, days)
        
        if df is not None and not df.empty:
            # Rename the 'price' column to the asset ID for easy identification
            all_prices[asset_id] = df['price']

    # Handle the case where no data was successfully loaded
    if not all_prices:
        return None

    # Concatenate all price series into a single DataFrame
    price_df = pd.DataFrame(all_prices)
    
    # Crucial step: Drop rows with any missing values to ensure all assets are aligned on the same dates
    # This prevents errors in correlation and portfolio calculations.
    price_df.dropna(inplace=True)
    
    return price_df

# --- PORTFOLIO CALCULATIONS ---
def calculate_portfolio_metrics(
    price_df: pd.DataFrame, 
    weights: List[float], 
    risk_free_rate: float = 0.0
) -> Optional[Dict[str, float or str]]:
    """
    Calculates the key portfolio metrics (Annualized Return, Volatility, Sharpe Ratio, Correlation).

    Args:
        price_df (pd.DataFrame): Aligned DataFrame of asset prices.
        weights (List[float]): The allocation weights for each asset.
        risk_free_rate (float): Annual risk-free rate for Sharpe Ratio calculation.

    Returns:
        Optional[Dict[str, float or str]]: Dictionary of portfolio metrics.
    """
    if price_df.empty or len(weights) != price_df.shape[1]:
        return None

    # 1. Calculate Logarithmic Daily Returns
    # Log returns are generally preferred for portfolio calculations (easier aggregation).
    log_returns = np.log(price_df / price_df.shift(1)).dropna()

    # 2. Annualization Constants
    TRADING_DAYS_PER_YEAR = 365 # Using 365 for 24/7 crypto markets

    # 3. Portfolio Return
    asset_expected_returns_annual = log_returns.mean() * TRADING_DAYS_PER_YEAR
    portfolio_return_annual = np.sum(asset_expected_returns_annual * weights)

    # 4. Portfolio Volatility (Risk)
    cov_matrix_daily = log_returns.cov()
    # Volatility is calculated using the covariance matrix and weights: sqrt(W^T * Cov * W * Days)
    portfolio_volatility_annual = np.sqrt(
        np.dot(weights, np.dot(cov_matrix_daily * TRADING_DAYS_PER_YEAR, weights))
    )

    # 5. Sharpe Ratio
    sharpe_ratio = (portfolio_return_annual - risk_free_rate) / portfolio_volatility_annual
    
    # 6. Correlation Matrix (HTML formatted for easy Streamlit display)
    correlation_matrix = log_returns.corr().to_html(classes='table table-striped', float_format='{:.2f}'.format)


    return {
        "Annual Return (%)": portfolio_return_annual * 100,
        "Annual Volatility (%)": portfolio_volatility_annual * 100,
        "Sharpe Ratio": sharpe_ratio,
        "Correlation Matrix": correlation_matrix
    }
def calculate_portfolio_performance_series(price_df: pd.DataFrame, weights: List[float]) -> pd.Series:
    """
    Calculates the time series of the portfolio's cumulative value.
    This series is normalized to start at 1.0.
    """
    if price_df.empty or len(weights) != price_df.shape[1]:
        return pd.Series(dtype=float)

    # Daily log returns are required
    log_returns = np.log(price_df / price_df.shift(1)).dropna()

    # Calculate daily portfolio return (weighted sum of asset returns)
    portfolio_daily_return = log_returns.dot(weights)
    
    # Calculate cumulative performance: exp(cumulative sum of log returns)
    cumulative_performance = np.exp(portfolio_daily_return.cumsum())
    
    # The time series index will be the same as the log_returns index (starts one day after prices)
    return cumulative_performance

# --- UTILITY FUNCTION: INDIVIDUAL ASSET RETURNS ---
def calculate_individual_cumulative_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the time series of cumulative value for each individual asset.
    This series is normalized to start at 1.0 (Day 0).
    """
    # Normalization: Current Price / First Price
    # This allows for easy comparison with the portfolio's performance
    normalized_prices = price_df / price_df.iloc[0]
    
    return normalized_prices.rename(columns={col: col for col in normalized_prices.columns})

