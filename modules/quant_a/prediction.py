import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Tuple, Optional

class PricePredictor:
    """
    Simple Machine Learning model to forecast asset prices.
    Uses Linear Regression on lagged price features.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.model = LinearRegression()

    def prepare_data(self, lags: int = 3) -> pd.DataFrame:
        """
        Creates lag features (Price t-1, Price t-2...) for the model.
        """
        df_ml = self.df[['price']].copy()
        for lag in range(1, lags + 1):
            df_ml[f'lag_{lag}'] = df_ml['price'].shift(lag)
        
        # Drop rows with NaN created by shifting
        return df_ml.dropna()

    def train_and_predict(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Trains the model and predicts the next day's price.
        
        Returns:
            Tuple: (Predicted Price, R^2 Score)
        """
        data = self.prepare_data()
        
        if len(data) < 10:
            return None, None # Not enough data to train

        # Features (X) and Target (y)
        feature_cols = [col for col in data.columns if 'lag_' in col]
        X = data[feature_cols]
        y = data['price']

        # Train
        self.model.fit(X, y)
        
        # Score (R-squared)
        score = self.model.score(X, y)

        # Predict next step using the most recent data points
        # We need the last known prices to predict "tomorrow"
        last_row = self.df.iloc[-1]
        # Construct the input array manually based on lags
        # Example: if lags=3, we need [price_t, price_t-1, price_t-2]
        recent_features = []
        for i in range(len(feature_cols)):
             # We take data from the end of the original DF
             recent_features.append(self.df['price'].iloc[-(i+1)])
        
        # Reshape for sklearn (1 sample, n features)
        prediction_input = np.array(recent_features).reshape(1, -1)
        
        predicted_price = self.model.predict(prediction_input)[0]
        
        return predicted_price, score
