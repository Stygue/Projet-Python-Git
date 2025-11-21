import pandas as pd
import numpy as np

def calculate_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates daily percentage returns based on the 'price' column.
    """
    df = df.copy()
    df['returns'] = df['price'].pct_change().fillna(0)
    return df

def apply_buy_and_hold(df: pd.DataFrame) -> pd.DataFrame:
    """
    Simulates a Buy and Hold strategy.
    Adds a 'cum_return_bh' column representing the cumulative strategy performance.
    """
    # Ensure returns exist
    if 'returns' not in df.columns:
        df = calculate_daily_returns(df)
    
    # Cumulative return formula: (1 + r1) * (1 + r2) ...
    df['cum_return_bh'] = (1 + df['returns']).cumprod()
    return df

def apply_sma_crossover(df: pd.DataFrame, short_window: int = 10, long_window: int = 30) -> pd.DataFrame:
    """
    Simulates a Simple Moving Average (SMA) Crossover strategy.
    
    Logic:
    - Buy (1) when Short SMA > Long SMA
    - Sell/Cash (0) when Short SMA < Long SMA
    
    Args:
        df (pd.DataFrame): Data containing 'price'.
        short_window (int): Window for the fast moving average.
        long_window (int): Window for the slow moving average.
    """
    if 'returns' not in df.columns:
        df = calculate_daily_returns(df)

    # 1. Calculate Indicators
    df['SMA_Short'] = df['price'].rolling(window=short_window).mean()
    df['SMA_Long'] = df['price'].rolling(window=long_window).mean()

    # 2. Generate Signals
    # np.where(condition, value_if_true, value_if_false)
    df['signal'] = np.where(df['SMA_Short'] > df['SMA_Long'], 1, 0)

    # 3. Shift signal to avoid look-ahead bias
    # We trade TODAY based on YESTERDAY's signal
    df['position'] = df['signal'].shift(1)

    # 4. Calculate Strategy Returns
    df['strategy_returns'] = df['position'] * df['returns']
    df['cum_return_sma'] = (1 + df['strategy_returns']).cumprod()

    return df
