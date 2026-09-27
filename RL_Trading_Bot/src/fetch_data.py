import os
import pandas as pd
import yfinance as yf
import numpy as np

# Set up paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def compute_rsi(data: pd.Series, window: int = 14) -> pd.Series:
    """Calculates the Relative Strength Index (RSI)."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def fetch_and_prepare_data(ticker: str = "NVDA", start_date: str = "2018-01-01", end_date: str = "2024-01-01"):
    print(f"Downloading historical data for {ticker}...")
    
    # Download raw data from Yahoo Finance
    df = yf.download(ticker, start=start_date, end=end_date)
    
    # yfinance sometimes returns MultiIndex columns. Flatten them if necessary.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df.dropna(inplace=True)
    
    print("Calculating technical indicators...")
    
    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Relative Strength Index (RSI)
    df['RSI_14'] = compute_rsi(df['Close'])
    
    # Moving Average Convergence Divergence (MACD)
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # ---------------------------------------------------------
    # CRITICAL MACHINE LEARNING FIX (Authentic Developer Note)
    # ---------------------------------------------------------
    # TODO(bhaskar): My first PPO agent failed completely here.
    # It turns out Neural Networks hate absolute stock prices because they are 
    # non-stationary (e.g., NVDA went from $40 to $900). 
    # I am converting the features to log returns and percentage changes 
    # so the RL agent sees normalized, stationary data instead.
    
    df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
    df['Volume_Change'] = df['Volume'].pct_change()
    
    # Drop the NaN rows created by the rolling windows and shifts
    df.dropna(inplace=True)
    
    # Save to CSV for the Gym Environment to consume later
    output_path = os.path.join(DATA_DIR, f"{ticker}_training_data.csv")
    df.to_csv(output_path)
    
    print(f"Data pipeline complete. Saved to {output_path}")
    print(f"Total valid trading days for RL environment: {len(df)}")
    
    return df

if __name__ == "__main__":
    # Using NVDA because its high volatility is perfect for training a trading agent
    fetch_and_prepare_data()
