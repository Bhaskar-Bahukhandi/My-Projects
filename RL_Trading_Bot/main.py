import argparse
import os
import sys

# Ensure local imports work cleanly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.fetch_data import fetch_and_prepare_data
from src.train import train_agent
from src.backtest import run_backtest
from src.tune import run_study

def main():
    parser = argparse.ArgumentParser(description="RL Trading Bot Command Line Interface")
    parser.add_argument(
        "action", 
        choices=["fetch", "train", "tune", "backtest"], 
        help="The action to perform: fetch (data), train (PPO), tune (Optuna), backtest (Evaluate)."
    )
    
    args = parser.parse_args()
    
    if args.action == "fetch":
        print("\n--- Running Data Pipeline ---")
        fetch_and_prepare_data()
    elif args.action == "train":
        print("\n--- Starting PPO Training ---")
        train_agent()
    elif args.action == "tune":
        print("\n--- Starting Optuna Tuning ---")
        run_study()
    elif args.action == "backtest":
        print("\n--- Running Backtest ---")
        run_backtest()

if __name__ == "__main__":
    main()
