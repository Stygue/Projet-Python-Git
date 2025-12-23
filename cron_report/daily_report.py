import pandas as pd
import numpy as np
import os
from datetime import datetime
from data_handling.api_connector import CryptoDataFetcher
# On importe la logique métier pour éviter de réécrire les calculs
from modules.quant_b.portfolio_logic import (
    calculate_portfolio_metrics, 
    calculate_rebalanced_portfolio_with_quantities
)

def generate_report():
    assets = ["bitcoin", "ethereum", "solana"]
    report_dir = "reports"
    if not os.path.exists(report_dir): os.makedirs(report_dir)
        
    now = datetime.now()
    report_path = f"{report_dir}/quant_full_report_{now.strftime('%Y-%m-%d')}.txt"
    
    # Paramètres de simulation (similaires à l'interface UI)
    days_history = "365"
    target_weights = [0.4, 0.3, 0.3] # 40% BTC, 30% ETH, 30% SOL
    
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"====================================================\n")
            f.write(f"📊 SYSTEM-WIDE QUANT REPORT - {now.strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"====================================================\n\n")

            # --- PARTIE 1 : ANALYSE QUANT A (ASSETS & IA) ---
            f.write(f"🛡️ SECTION 1: INDIVIDUAL ASSET ANALYSIS (Quant A)\n")
            f.write(f"----------------------------------------------------\n")
            
            price_series_list = []
            for asset in assets:
                df = CryptoDataFetcher.get_historical_data(asset, days=days_history)
                if df is not None:
                    # Stockage pour Quant B plus tard
                    price_series_list.append(df['price'])
                    
                    # Métriques de base
                    close_p = df['price'].iloc[-1]
                    perf_24h = ((close_p - df['price'].iloc[-2]) / df['price'].iloc[-2]) * 100
                    
                    # Simulation simplifiée SMA Crossover (Quant A)
                    sma_20 = df['price'].rolling(20).mean()
                    sma_50 = df['price'].rolling(50).mean()
                    signal = "BUY" if sma_20.iloc[-1] > sma_50.iloc[-1] else "SELL"
                    
                    # Simulation Prédiction IA (Fictive ici, car nécessite l'entraînement)
                    # Dans ton code réel, tu appellerais ta fonction de prédiction
                    predicted_change = np.random.uniform(-2, 2) 
                    
                    f.write(f"Asset: {asset.upper()}\n")
                    f.write(f" • Price: ${close_p:,.2f} ({perf_24h:+.2f}%)\n")
                    f.write(f" • Quant A Signal (SMA): {signal}\n")
                    f.write(f" • IA Forecast (Next 24h): {predicted_change:+.2f}%\n\n")

            # --- PARTIE 2 : GESTION DE PORTEFEUILLE (Quant B) ---
            f.write(f"💼 SECTION 2: PORTFOLIO PERFORMANCE (Quant B)\n")
            f.write(f"----------------------------------------------------\n")
            
            if len(price_series_list) == len(assets):
                price_df = pd.concat(price_series_list, axis=1)
                price_df.columns = assets
                price_df.dropna(inplace=True)

                # Utilisation de tes fonctions de calcul (Quant B)
                portfolio_val, amounts_df = calculate_rebalanced_portfolio_with_quantities(
                    price_df, target_weights, frequency='W'
                )
                
                metrics = calculate_portfolio_metrics(price_df, target_weights)
                
                f.write(f"Strategy: Weekly Rebalancing\n")
                f.write(f" • Annualized Return: {metrics['Annual Return (%)']:.2f}%\n")
                f.write(f" • Portfolio Volatility: {metrics['Annual Volatility (%)']:.2f}%\n")
                f.write(f" • Sharpe Ratio: {metrics['Sharpe Ratio']:.2f}\n\n")
                
                f.write(f"🔄 LATEST QUANTITY ADJUSTMENTS (Rebalancing):\n")
                for asset in assets:
                    initial_qty = amounts_df[asset].iloc[0]
                    current_qty = amounts_df[asset].iloc[-1]
                    change = ((current_qty - initial_qty) / initial_qty) * 100
                    f.write(f" • {asset.upper()}: {current_qty:.4f} units ({change:+.2f}% total drift)\n")

            f.write(f"\n[End of Quant System Report]")
            
        print(f"✅ Full Report generated: {report_path}")

    except Exception as e:
        print(f"❌ Error during report generation: {e}")

if __name__ == "__main__":
    generate_report()