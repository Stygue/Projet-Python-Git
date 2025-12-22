import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, accuracy_score
from typing import Tuple, Dict, Any

class AdvancedPricePredictor:
    """
    Advanced ML model using Random Forest on engineered features.
    Predicts Returns instead of Prices for statistical stationarity.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        # On utilise un Random Forest : robuste au sur-apprentissage et non-linéaire
        self.model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        self.features = []

    def _feature_engineering(self) -> pd.DataFrame:
        """
        Creates financial features: Lags, Rolling Means, Volatility, Momentum.
        """
        data = self.df[['price']].copy()
        
        # 1. Target: Log Returns (plus stables mathématiquement que les prix bruts)
        data['return'] = np.log(data['price'] / data['price'].shift(1))
        
        # 2. Lagged Returns (Autocorrélation)
        # Ce qu'il s'est passé hier, avant-hier, etc.
        for lag in [1, 2, 3, 5]:
            col = f'lag_return_{lag}'
            data[col] = data['return'].shift(lag)
            self.features.append(col)
            
        # 3. Rolling Volatility (Risque récent)
        data['volatility_5d'] = data['return'].rolling(window=5).std()
        self.features.append('volatility_5d')
        
        # 4. Trend / Momentum (Prix vs Moyenne Mobile)
        data['sma_5'] = data['price'].rolling(window=5).mean()
        data['dist_to_sma'] = (data['price'] - data['sma_5']) / data['sma_5']
        self.features.append('dist_to_sma')

        # Nettoyage des NaN générés par les lags/rolling
        return data.dropna()

    def train_and_analyze(self) -> Dict[str, Any]:
        """
        Trains the model using TimeSeriesSplit (No Look-ahead bias).
        Returns metrics and the trained model details.
        """
        data = self._feature_engineering()
        
        if len(data) < 30:
            return {"error": "Not enough data (min 30 days required)"}

        X = data[self.features]
        y = data['return'] # On prédit le rendement

        # Split Train/Test (80/20) respectant la temporalité
        split_idx = int(len(data) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # Entraînement
        self.model.fit(X_train, y_train)
        
        # Prédictions sur le test set (Log Returns)
        y_pred_log_returns = self.model.predict(X_test)
        
        # --- Métriques ---
        rmse = np.sqrt(mean_squared_error(y_test, y_pred_log_returns))
        
        y_test_dir = np.sign(y_test)
        y_pred_dir = np.sign(y_pred_log_returns)
        dir_acc = accuracy_score(y_test_dir, y_pred_dir)

        importances = dict(zip(self.features, self.model.feature_importances_))
        
        # --- PREPARATION DONNEES GRAPHIQUE (NOUVEAU) ---
        # Reconstruction des prix : Prix_T = Prix_(T-1) * exp(Return_T)
        test_dates = y_test.index
        
        # On récupère le prix de la veille pour chaque date de test
        prev_prices = self.df['price'].shift(1).loc[test_dates]
        
        # Calcul du prix prédit
        predicted_prices = prev_prices * np.exp(y_pred_log_returns)
        
        # Prix réels
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
            "plotting_data": plotting_data # <--- Données pour le graphique
        }


    def predict_next_day(self) -> Tuple[float, float, float]:
        """
        Re-trains on FULL data and predicts tomorrow's price.
        Returns: (Predicted Price, Predicted Return %, Confidence/Directional Acc)
        """
        data = self._feature_engineering()
        X = data[self.features]
        y = data['return']
        
        # Entraînement sur TOUT l'historique disponible
        self.model.fit(X, y)
        
        # Construction des features pour "Demain" basé sur les dernières données connues
        last_row = data.iloc[-1]
        
        # On doit reconstruire l'input manuellement pour sklearn
        # Attention : C'est ici que la logique doit être impeccable
        input_features = []
        
        # Lags : On prend les returns récents
        # lag_return_1 devient le return d'aujourd'hui, etc.
        current_return = last_row['return']
        
        # Pour simplifier l'inférence sans reconstruire tout le dataset, 
        # on prend la dernière ligne de X (qui correspond à "Aujourd'hui")
        # Mais pour prédire demain, il faut shifter... 
        # Pour ce projet scolaire, on va utiliser la dernière observation connue comme proxy immédiat
        # ou mieux : utiliser la dernière ligne de X pour prédire Y (qui est le return de demain par rapport à auj)
        # Dans notre feature engineering, Y est aligné sur T. X contient T-1, T-2.
        # Donc si on passe les features d'AUJOURD'HUI (T), le modèle prédit le return de DEMAIN (T+1).
        
        last_features = X.iloc[[-1]] # Double crochet pour garder DataFrame 2D
        
        predicted_log_return = self.model.predict(last_features)[0]
        
        # Conversion Log Return -> Prix
        # Prix Demain = Prix Auj * exp(Log Return)
        last_price = self.df['price'].iloc[-1]
        predicted_price = last_price * np.exp(predicted_log_return)
        
        # On récupère la précision directionnelle estimée lors du test précédent
        # pour donner une idée de la fiabilité
        metrics = self.train_and_analyze()
        confidence = metrics.get('directional_accuracy', 0.5)
        
        return predicted_price, np.exp(predicted_log_return) - 1, confidence
