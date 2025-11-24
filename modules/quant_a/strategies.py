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

def apply_rsi_strategy(df: pd.DataFrame, window: int = 14, lower_bound: int = 30, upper_bound: int = 70) -> pd.DataFrame:
    """
    Simulates a Mean Reversion strategy using the Relative Strength Index (RSI).
    
    Logic:
    - Buy (1) when RSI < lower_bound (Oversold condition).
    - Sell/Cash (0) when RSI > upper_bound (Overbought condition).
    - Hold previous position between bounds.
    
    Args:
        df (pd.DataFrame): Data containing 'price'.
        window (int): Lookback period for RSI (standard is 14).
        lower_bound (int): Threshold to buy (standard is 30).
        upper_bound (int): Threshold to sell (standard is 70).
    """
    if 'returns' not in df.columns:
        df = calculate_daily_returns(df)

    # 1. Calculate RSI
    delta = df['price'].diff()
    
    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    # Calculate Exponential Moving Average (Wilder's Smoothing)
    avg_gain = gain.ewm(span=window, adjust=False).mean()
    avg_loss = loss.ewm(span=window, adjust=False).mean()

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    # Handle division by zero if avg_loss is 0
    rs = rs.replace([np.inf, -np.inf], 0)
    
    df['RSI'] = 100 - (100 / (1 + rs))

    # 2. Generate Signals
    # Initialize signal column with NaN
    df['signal'] = np.nan
    
    # Buy signal (1) when RSI drops below lower bound
    df.loc[df['RSI'] < lower_bound, 'signal'] = 1
    
    # Sell signal (0) when RSI rises above upper bound
    df.loc[df['RSI'] > upper_bound, 'signal'] = 0
    
    # Forward fill the signals (Hold position between zones)
    df['signal'] = df['signal'].ffill().fillna(0)

    # 3. Shift signal (Trade tomorrow based on today's RSI)
    df['position'] = df['signal'].shift(1)

    # 4. Calculate Strategy Returns
    df['strategy_returns'] = df['position'] * df['returns']
    df['cum_return_rsi'] = (1 + df['strategy_returns']).cumprod()

    return df
