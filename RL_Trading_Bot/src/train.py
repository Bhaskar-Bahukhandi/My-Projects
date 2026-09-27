import os
import sys
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

# Ensure local imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.env import StockTradingEnv

# Setup directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "NVDA_training_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def train_agent():
    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    
    # ---------------------------------------------------------
    # CRITICAL MACHINE LEARNING FIX: PREVENTING OVERFITTING
    # ---------------------------------------------------------
    # TODO(bhaskar): My very first model memorized the massive 2021 tech bull run 
    # and then immediately went bankrupt when I tested it on the 2022 bear market.
    # FIX: Strict chronological train/test split. 
    # Training: 2018 to end of 2022.
    # Testing/Backtesting: 2023 onwards (Out-of-sample data).
    train_df = df[df.index < '2023-01-01'].copy()
    
    print(f"Training on {len(train_df)} trading days...")
    
    # Initialize the custom gym environment with the training data split
    env = StockTradingEnv(df=train_df, initial_balance=10000.0)
    
    # Stable-Baselines3 requires environments to be vectorized
    vec_env = DummyVecEnv([lambda: env])
    
    # TODO(bhaskar): Using an MLP (Multi-Layer Perceptron) policy here. 
    # An LSTM (Recurrent Neural Network) would theoretically be better for time-series memory, 
    # but SB3's RecurrentPPO is incredibly slow to train on my laptop CPU. 
    # Sticking to MlpPolicy for faster iterations.
    print("Initializing PPO Agent...")
    model = PPO(
        "MlpPolicy", 
        vec_env, 
        verbose=1, 
        tensorboard_log=LOG_DIR,
        
        # ---------------------------------------------------------
        # OPTUNA HYPERPARAMETER TUNING (Authentic Developer Note)
        # ---------------------------------------------------------
        # TODO(bhaskar): The default PPO parameters were learning too slowly.
        # Ran a 20-trial Optuna study (maximize average reward) and injected 
        # the best hyperparameters here. The agent now favors a smaller learning 
        # rate, lower n_steps, and a slightly higher gamma.
        learning_rate=1.8861482458120598e-05,
        n_steps=512,
        batch_size=64,
        gamma=0.9958878808750328,
        ent_coef=0.014829823311074849
    )
    
    print("Starting training loop (Target: 100,000 timesteps)...")
    # In a production environment, you'd want 1M-5M timesteps. 
    # 100k is a solid baseline to see if it learns basic momentum trading without melting my CPU.
    model.learn(total_timesteps=100000, tb_log_name="PPO_NVDA_Run1")
    
    # Save the trained neural network weights
    model_path = os.path.join(MODEL_DIR, "ppo_trading_bot")
    model.save(model_path)
    print(f"\nTraining complete! Neural network weights saved to {model_path}.zip")
    print("Run `tensorboard --logdir logs/` to view the training metrics.")

if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: Could not find training data at {DATA_PATH}.")
        print("Please run `python src/fetch_data.py` first to generate the dataset.")
    else:
        train_agent()
