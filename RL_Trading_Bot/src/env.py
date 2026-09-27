import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class StockTradingEnv(gym.Env):
    """
    A Custom OpenAI Gymnasium Environment for Stock Trading.
    Simulates a portfolio where an RL agent can Buy, Sell, or Hold based on historical data.
    """
    metadata = {'render_modes': ['human']}

    def __init__(self, df: pd.DataFrame, initial_balance: float = 10000.0):
        super(StockTradingEnv, self).__init__()
        
        # We reset the index so we can iterate cleanly via self.current_step
        self.df = df.reset_index(drop=True)
        self.initial_balance = initial_balance
        
        # Action Space: 0 = Hold, 1 = Buy, 2 = Sell
        self.action_space = spaces.Discrete(3)
        
        # Observation Space: We feed the agent the 7 technical indicators we engineered,
        # plus 3 portfolio state variables (balance, shares held, net worth).
        # Total features = 10
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32
        )
        
        # TODO(bhaskar): Real-world constraint! 99% of student trading bots fail in production
        # because they assume trades are free. I am adding a 0.1% commission fee per trade 
        # to force the agent to find HIGH PROBABILITY setups rather than high-frequency scalping.
        self.commission_fee = 0.001 
        
        self.current_step = 0
        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance
        
    def reset(self, seed=None, options=None):
        """Resets the environment for a new training episode."""
        super().reset(seed=seed)
        self.current_step = 0
        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance
        return self._next_observation(), {}
        
    def _next_observation(self):
        """Constructs the state array for the neural network."""
        obs = np.array([
            self.df.loc[self.current_step, 'SMA_20'],
            self.df.loc[self.current_step, 'SMA_50'],
            self.df.loc[self.current_step, 'RSI_14'],
            self.df.loc[self.current_step, 'MACD'],
            self.df.loc[self.current_step, 'MACD_Signal'],
            self.df.loc[self.current_step, 'Log_Return'],
            self.df.loc[self.current_step, 'Volume_Change'],
            self.balance,
            self.shares_held,
            self.net_worth
        ], dtype=np.float32)
        
        # Failsafe: Neural networks will output NaNs if fed NaNs.
        return np.nan_to_num(obs)
        
    def step(self, action):
        """Executes the agent's chosen action and calculates the reward."""
        current_price = self.df.loc[self.current_step, 'Close']
        prev_net_worth = self.net_worth
        
        # 1. Execute action
        if action == 1: # BUY
            # Go all-in (buy as many shares as balance allows, accounting for fees)
            shares_bought = int(self.balance / (current_price * (1 + self.commission_fee)))
            if shares_bought > 0:
                self.balance -= shares_bought * current_price * (1 + self.commission_fee)
                self.shares_held += shares_bought
                
        elif action == 2: # SELL
            if self.shares_held > 0:
                self.balance += self.shares_held * current_price * (1 - self.commission_fee)
                self.shares_held = 0
                
        # 2. Update Net Worth
        self.net_worth = self.balance + (self.shares_held * current_price)
        
        # ---------------------------------------------------------
        # CRITICAL MACHINE LEARNING FIX: REWARD HACKING
        # ---------------------------------------------------------
        # TODO(bhaskar): In my first training run, the agent realized that because of the 0.1% 
        # commission fee, the safest mathematical move was to NEVER TRADE. It just held cash 
        # for 5 years and achieved a 0% return. 
        # FIX: The base reward is raw profit. BUT if the agent is holding pure cash while the 
        # market goes up, I penalize it for "Opportunity Cost". This forces it to take risks.
        
        reward = self.net_worth - prev_net_worth
        
        if self.shares_held == 0 and self.df.loc[self.current_step, 'Log_Return'] > 0:
            opportunity_cost = self.initial_balance * self.df.loc[self.current_step, 'Log_Return'] * 0.1
            reward -= opportunity_cost

        # 3. Advance time
        self.current_step += 1
        
        # 4. Check for Episode End
        terminated = bool(self.current_step >= len(self.df) - 1)
        
        # Bankrupt condition
        if self.net_worth <= 0:
            terminated = True
            reward -= 10000 # Massive penalty to discourage bankruptcy
            
        truncated = False
        info = {'net_worth': self.net_worth}
        
        return self._next_observation(), reward, terminated, truncated, info

    def render(self):
        """Terminal logger for backtesting."""
        print(f"Step: {self.current_step} | Net Worth: ${self.net_worth:.2f} | Shares: {self.shares_held} | Balance: ${self.balance:.2f}")
