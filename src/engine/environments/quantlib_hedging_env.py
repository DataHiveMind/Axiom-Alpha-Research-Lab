import gymnasium as gym
import numpy as np
import QuantLib as ql
from gymnasium import spaces

class QuantLibHedgingEnv(gym.Env):
    """
    A high-frequency execution environment for Delta Hedging.
    Uses QuantLib to price a European Option and calculates the required hedge.
    """
    def __init__(self, initial_price=100.0, strike=100.0, risk_free_rate=0.05, volatility=0.2):
        super().__init__()
        
        # State: [Current Price, Time to Maturity, Option Delta, Current Inventory]
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32)
        
        # Action: Continuous value representing the quantity of underlying to buy/sell
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)
        
        # QuantLib Setup
        self.today = ql.Date().todaysDate()
        ql.Settings.instance().evaluationDate = self.today
        
        self.spot_handle = ql.RelinkableQuoteHandle(ql.SimpleQuote(initial_price))
        self.rate_handle = ql.YieldTermStructureHandle(ql.FlatForward(self.today, risk_free_rate, ql.Actual360()))
        self.vol_handle = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(self.today, ql.NullCalendar(), volatility, ql.Actual360()))
        
        bsm_process = ql.BlackScholesProcess(self.spot_handle, self.rate_handle, self.vol_handle)
        
        # Define a standard European Call Option
        payoff = ql.PlainVanillaPayoff(ql.Option.Call, strike)
        exercise = ql.EuropeanExercise(self.today + ql.Period(30, ql.Days))
        self.option = ql.VanillaOption(payoff, exercise)
        self.option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))

        self.inventory = 0.0

    def step(self, action):
        # 1. Simulate market tick (In reality, this comes from kdb+/q)
        current_spot = self.spot_handle.value()
        new_spot = current_spot * np.exp(np.random.normal(0, 0.01))
        self.spot_handle.linkTo(ql.SimpleQuote(new_spot))
        
        # 2. Get true Greek from QuantLib
        true_delta = self.option.delta()
        
        # 3. Execute Trade (Action is our hedge ratio)
        trade_qty = action[0]
        transaction_cost = abs(trade_qty) * 0.001 * new_spot # 10 bps slippage
        
        self.inventory += trade_qty
        
        # 4. Calculate Reward: Penalize Delta mismatch AND transaction costs
        hedge_error = abs(true_delta - self.inventory)
        reward = - (hedge_error * 10.0) - transaction_cost
        
        # State representation for the agent
        state = np.array([new_spot, 30.0, true_delta, self.inventory], dtype=np.float32)
        
        return state, reward, False, False, {}

    def reset(self, seed=None):
        self.inventory = 0.0
        self.spot_handle.linkTo(ql.SimpleQuote(100.0))
        return np.array([100.0, 30.0, 0.5, 0.0], dtype=np.float32), {}