import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from stable_baselines3 import PPO

# Ensure local imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.env import StockTradingEnv

# Setup directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "NVDA_training_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "ppo_trading_bot.zip")

def run_backtest():
    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    
    # ---------------------------------------------------------
    # OUT-OF-SAMPLE VALIDATION
    # ---------------------------------------------------------
    # The golden rule of quant finance: NEVER test on data the model has seen.
    # We slice the dataframe to only include 2023 onwards.
    test_df = df[df.index >= '2023-01-01'].copy()
    
    if len(test_df) == 0:
        print("ERROR: Not enough data for backtesting. Check your date ranges.")
        return

    print(f"Backtesting on {len(test_df)} out-of-sample trading days...")
    
    # Initialize the environment with test data
    env = StockTradingEnv(df=test_df, initial_balance=10000.0)
    
    # Load the trained model
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Trained model not found at {MODEL_PATH}")
        print("Please run `python src/train.py` first.")
        return
        
    print("Loading trained PPO Agent...")
    model = PPO.load(MODEL_PATH)
    
    # Simulation loop
    obs, _ = env.reset()
    done = False
    
    # Tracking metrics for plotting
    portfolio_values = []
    dates = []
    
    print("Running simulation...")
    while not done:
        # deterministic=True ensures the agent picks the mathematical best action
        # instead of exploring randomly like it does during training.
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        
        portfolio_values.append(info['net_worth'])
        
        # env.current_step is advanced AFTER the step, so we use current_step - 1 for the date
        date_idx = env.current_step - 1
        if date_idx < len(test_df):
            dates.append(test_df.index[date_idx])
        
        done = terminated or truncated

    final_net_worth = portfolio_values[-1]
    roi = ((final_net_worth - 10000.0) / 10000.0) * 100
    
    # ---------------------------------------------------------
    # THE "BUY & HOLD" BASELINE TEST
    # ---------------------------------------------------------
    # TODO(bhaskar): If the bot can't beat simply buying the stock on day 1 and doing nothing, 
    # the RL agent is practically useless. This baseline is crucial for an honest evaluation.
    initial_price = test_df.iloc[0]['Close']
    final_price = test_df.iloc[-1]['Close']
    buy_hold_shares = 10000.0 / initial_price
    buy_hold_final = buy_hold_shares * final_price
    buy_hold_roi = ((buy_hold_final - 10000.0) / 10000.0) * 100

    print("\n" + "="*40)
    print("BACKTEST RESULTS (Out-of-Sample)")
    print("="*40)
    print(f"Initial Balance:     $10,000.00")
    print(f"Final Bot Value:     ${final_net_worth:,.2f} ({roi:+.2f}%)")
    print(f"Buy & Hold Value:    ${buy_hold_final:,.2f} ({buy_hold_roi:+.2f}%)")
    print("="*40)
    
    # In my first run, the bot massively underperformed Buy & Hold because NVDA went up 
    # 200% in 2023/2024, and taking ANY trades just resulted in paying commissions while 
    # missing out on the massive trend. A good reminder that AI isn't magic.

    # Plotting the results
    plt.figure(figsize=(12, 6))
    plt.plot(dates, portfolio_values, label=f"RL Trading Bot (ROI: {roi:.2f}%)", color='blue')
    
    # Simulate buy and hold curve over time
    buy_hold_curve = (10000.0 / initial_price) * test_df['Close']
    plt.plot(dates, buy_hold_curve[:len(dates)], label=f"Buy & Hold Baseline (ROI: {buy_hold_roi:.2f}%)", color='orange', linestyle='--')
             
    plt.title("RL Agent vs Buy & Hold (Out-of-Sample Validation)")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    chart_path = os.path.join(BASE_DIR, "backtest_results.png")
    plt.savefig(chart_path)
    print(f"\nSaved performance chart to {chart_path}")

if __name__ == "__main__":
    run_backtest()
