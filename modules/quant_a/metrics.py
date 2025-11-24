import pandas as pd
import numpy as np

def get_performance_summary(df: pd.DataFrame, col_name: str = 'price'):
    """
    Calculates performance metrics (Total Return, Volatility, Sharpe, Max Drawdown).
    Robust against division by zero and NaN values.
    """
    # 1. Basic Safety Checks
    if df is None or df.empty:
        return _empty_metrics()

    if col_name not in df.columns:
        # Fallback: try to find a valid column
        if 'strategy_returns' in df.columns:
            col_name = 'strategy_returns'
        elif 'returns' in df.columns:
            col_name = 'returns'
        elif 'price' in df.columns:
            col_name = 'price'
        else:
            return _empty_metrics()

    df = df.copy()
    df = df.sort_index()

    # 2. Determine Data Type (Price vs Returns)
    # Heuristic: If column name contains 'return', treat as percentage change.
    is_returns_data = 'return' in col_name

    if is_returns_data:
        # --- CASE A: INPUT IS RETURNS (e.g., 0.01 for 1%) ---
        # Clean the returns
        series_returns = pd.to_numeric(df[col_name], errors='coerce').fillna(0)
        series_returns = series_returns.replace([np.inf, -np.inf], 0)
        
        # Reconstruct a Synthetic Price (Base 100) for Drawdown calculation
        # Formula: 100 * (1 + r1) * (1 + r2)...
        series_prices = 100 * (1 + series_returns).cumprod()
        
    else:
        # --- CASE B: INPUT IS PRICE (e.g., 50000 USD) ---
        series_prices = pd.to_numeric(df[col_name], errors='coerce')
        series_prices = series_prices.dropna()
        
        if len(series_prices) < 2:
            return _empty_metrics()
            
        # Calculate Returns
        series_returns = series_prices.pct_change().fillna(0)
        series_returns = series_returns.replace([np.inf, -np.inf], 0)

    # 3. Calculate Metrics
    
    # A. Total Return
    # We use the synthetic or real price evolution
    start_price = series_prices.iloc[0]
    end_price = series_prices.iloc[-1]
    
    if start_price <= 0:
        total_return = 0.0
    else:
        total_return = (end_price - start_price) / start_price

    # B. Volatility (Annualized)
    # Standard deviation of daily returns * sqrt(365) for crypto
    volatility = series_returns.std() * np.sqrt(365)

    # C. Sharpe Ratio
    # Assuming Risk-Free Rate = 0 for simplicity in crypto context
    avg_annual_return = series_returns.mean() * 365
    
    if volatility == 0 or pd.isna(volatility):
        sharpe_ratio = 0.0
    else:
        sharpe_ratio = avg_annual_return / volatility

    # D. Max Drawdown
    # Calculate rolling maximum of the price series
    rolling_max = series_prices.cummax()
    
    # Avoid division by zero if price is 0 (unlikely but possible)
    rolling_max = rolling_max.replace(0, 1e-9)
    
    drawdown = (series_prices - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # 4. Final Cleanup
    return {
        "Total Return": _clean_val(total_return),
        "Volatility": _clean_val(volatility),
        "Sharpe Ratio": _clean_val(sharpe_ratio),
        "Max Drawdown": _clean_val(max_drawdown)
    }

def _clean_val(val):
    """Helper to remove NaN/Inf from final output."""
    if pd.isna(val) or np.isinf(val):
        return 0.0
    return val

def _empty_metrics():
    return {
        "Total Return": 0.0,
        "Volatility": 0.0,
        "Sharpe Ratio": 0.0,
        "Max Drawdown": 0.0
    }
