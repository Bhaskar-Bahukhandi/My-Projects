import os
import sys
import pandas as pd
import optuna
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy

# Ensure local imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.env import StockTradingEnv

# Setup directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "NVDA_training_data.csv")

def optimize_ppo(trial):
    """
    Optuna objective function to find the absolute best PPO hyperparameters.
    """
    # 1. Let Optuna suggest hyperparameter values within standard ML ranges
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-3, log=True)
    n_steps = trial.suggest_categorical("n_steps", [512, 1024, 2048, 4096])
    batch_size = trial.suggest_categorical("batch_size", [64, 128, 256])
    gamma = trial.suggest_float("gamma", 0.9, 0.9999, log=True) # Discount factor
    ent_coef = trial.suggest_float("ent_coef", 0.0001, 0.1, log=True) # Exploration rate
    
    # Stable-Baselines3 requirement: n_steps must be evenly divisible by batch_size
    if n_steps % batch_size != 0:
        raise optuna.exceptions.TrialPruned()

    # 2. Setup Environment
    # We load the data fresh for each trial, but only use the training split (Pre-2023)
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    train_df = df[df.index < '2023-01-01'].copy()
    
    env = DummyVecEnv([lambda: StockTradingEnv(df=train_df, initial_balance=10000.0)])
    
    # 3. Initialize Model with suggested parameters
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=learning_rate,
        n_steps=n_steps,
        batch_size=batch_size,
        gamma=gamma,
        ent_coef=ent_coef,
        verbose=0 # Turn off logs so it doesn't flood the terminal during tuning
    )
    
    # ---------------------------------------------------------
    # COMPUTE CONSTRAINT FIX
    # ---------------------------------------------------------
    # TODO(bhaskar): A proper hyperparameter search requires 100+ trials of 100k+ steps. 
    # Without a dedicated GPU cluster, this would take 12+ hours on my laptop.
    # I am limiting each trial to 15,000 steps. It's not enough to fully train the model, 
    # but it IS enough to get a "directional sense" of which learning rate converges fastest.
    
    # 4. Train Model briefly
    try:
        model.learn(total_timesteps=15000)
    except Exception as e:
        # Sometimes extreme hyperparameters cause mathematical NaNs. Prune the trial.
        return -10000.0
    
    # 5. Evaluate Model
    # We test the model by letting it trade for 3 episodes and taking the average reward
    mean_reward, _ = evaluate_policy(model, env, n_eval_episodes=3)
    
    return mean_reward

def run_study():
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: Could not find training data at {DATA_PATH}.")
        return

    print("Starting Optuna Hyperparameter Optimization...")
    print("This will take a few minutes...")
    
    # We want to MAXIMIZE the reward (portfolio value)
    study = optuna.create_study(direction="maximize")
    
    # Running 20 trials due to local compute limits
    study.optimize(optimize_ppo, n_trials=20)
    
    print("\n" + "="*40)
    print("OPTUNA STUDY COMPLETE")
    print("="*40)
    print(f"Best Trial Score (Avg Reward): {study.best_value:.2f}")
    print("Best Hyperparameters:")
    for key, value in study.best_params.items():
        print(f"  {key}: {value}")
        
    print("\n(Note: You can copy these best parameters back into src/train.py to build the final model!)")

if __name__ == "__main__":
    run_study()
