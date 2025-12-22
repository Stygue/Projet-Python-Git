import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, accuracy_score
from typing import Tuple, Dict, Any

class AdvancedPricePredictor:
    """
    Prediction model using Random Forest.
    We predict returns instead of raw prices to have more stable data.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        # We use Random Forest because it handles complex relationships well
        # and avoids "memorizing" the data (overfitting).
        self.model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        self.features = []

    def _feature_engineering(self) -> pd.DataFrame:
        """
        Creating indicators to help the model learn:
        - Recent history (Lags)
        - Volatility
        - Trend (Moving Average)
        """
        data = self.df[['price']].copy()
        
        # 1. Target: Log Returns
        # We prefer predicting a percentage change rather than a raw price (e.g., $60k).
        # This is mathematically easier for the model to handle.
        data['return'] = np.log(data['price'] / data['price'].shift(1))
        
        # 2. Lags (What happened before)
        # The model looks at returns from 1 day ago, 2 days ago, etc.
        for lag in [1, 2, 3, 5]:
            col = f'lag_return_{lag}'
            data[col] = data['return'].shift(lag)
            self.features.append(col)
            
        # 3. Volatility (Is the market moving a lot?)
        # Standard deviation over the last 5 days.
        data['volatility_5d'] = data['return'].rolling(window=5).std()
        self.features.append('volatility_5d')
        
        # 4. Trend (Price vs Average)
        # Are we above or below the recent average?
        data['sma_5'] = data['price'].rolling(window=5).mean()
        data['dist_to_sma'] = (data['price'] - data['sma_5']) / data['sma_5']
        self.features.append('dist_to_sma')

        # We drop the first few rows that contain NaNs (due to previous calculations)
        return data.dropna()

    def train_and_analyze(self) -> Dict[str, Any]:
        """
        Trains the model on a part of the data and tests it on the end.
        Allows us to check if the model works well on data it has never seen.
        """
        data = self._feature_engineering()
        
        if len(data) < 30:
            return {"error": "Not enough data (minimum 30 days required)"}

        X = data[self.features]
        y = data['return'] # We try to guess the return

        # Chronological Split (Train 80% / Test 20%)
        # IMPORTANT: We do not shuffle the data. We must respect the timeline 
        # to avoid "cheating" by using the future to predict the past.
        split_idx = int(len(data) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # Training the model
        self.model.fit(X_train, y_train)
        
        # Testing the model (Predictions)
        y_pred_log_returns = self.model.predict(X_test)
        
        # --- Calculating Scores ---
        
        # RMSE: The average error of the model
        rmse = np.sqrt(mean_squared_error(y_test, y_pred_log_returns))
        
        # Directional Accuracy: Did we correctly predict if it goes UP or DOWN?
        y_test_dir = np.sign(y_test)
        y_pred_dir = np.sign(y_pred_log_returns)
        dir_acc = accuracy_score(y_test_dir, y_pred_dir)

        # Feature Importance: What helped the model the most?
        importances = dict(zip(self.features, self.model.feature_importances_))
        
        # --- Graph Preparation ---
        # We must transform predicted returns back into "Real Prices" for display
        test_dates = y_test.index
        
        # Previous day's price (T-1)
        prev_prices = self.df['price'].shift(1).loc[test_dates]
        
        # Formula: Predicted Price = Yesterday's Price * exp(Predicted Return)
        predicted_prices = prev_prices * np.exp(y_pred_log_returns)
        actual_prices = self.df.loc[test_dates, 'price']
        
        plotting_data = pd.DataFrame({
            'Actual': actual_prices,
            'Predicted': predicted_prices
        })

        return {
            "rmse": rmse,
            "directional_accuracy": dir_acc,
            "feature_importance": importances,
            "test_data_size": len(y_test),
            "plotting_data": plotting_data
        }


    def predict_next_day(self) -> Tuple[float, float, float]:
        """
        Re-trains the model on ALL available data to predict tomorrow.
        Returns: (Predicted Price, % Change, Confidence Index)
        """
        data = self._feature_engineering()
        X = data[self.features]
        y = data['return']
        
        # We re-train on the full history to be as up-to-date as possible
        self.model.fit(X, y)
        
        # To predict tomorrow, we use today's data (the last row)
        last_features = X.iloc[[-1]] 
        
        # The model predicts tomorrow's Log Return
        predicted_log_return = self.model.predict(last_features)[0]
        
        # Conversion to Price: Price Tomorrow = Price Today * exp(Predicted Return)
        last_price = self.df['price'].iloc[-1]
        predicted_price = last_price * np.exp(predicted_log_return)
        
        # We use the accuracy calculated during the previous test as a "confidence index"
        metrics = self.train_and_analyze()
        confidence = metrics.get('directional_accuracy', 0.5)
        
        return predicted_price, np.exp(predicted_log_return) - 1, confidence
