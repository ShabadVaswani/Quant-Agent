import abc
import numpy as np
import pandas as pd
import scipy
from scipy.stats import norm
from typing import Any, List, Dict, Optional, Union
import math
from data_fetcher import get_stock_prices

class FinancialInstrument(abc.ABC):
    """
    Abstract base class for all financial instruments.
    """

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.historical_data: Optional[pd.DataFrame] = None

    def load_historical_data(self, data: pd.DataFrame):
        """Inject historical data into the instrument."""
        self.historical_data = data

    @abc.abstractmethod
    def calculate_risk(self) -> float:
        """Calculate the risk associated with this instrument."""
        pass

    @abc.abstractmethod
    def get_current_price(self) -> float:
        """Return the current price, typically from the injected data."""
        pass


    def __str__(self):
        return f"{self.__class__.__name__}(ticker={self.ticker})"

class Stock(FinancialInstrument):
    """
    Represents a specific stock instrument.
    """

    def calculate_risk(self, confidence_level: float = 0.95, days: int = 1, num_simulations: int = 10000) -> float:
        """
        Calculate risk for the stock using Monte Carlo simulation.
        Returns the Value at Risk (VaR).
        """
        if self.historical_data is None or self.historical_data.empty or len(self.historical_data) < 2:
            return 0.0

        # 1. Get current price and volatility
        S = self.get_current_price()
        vol = self.calculate_historical_volatility()
        
        # 2. Simulate future prices
        # We assume daily returns are normally distributed
        # drift = 0 (simplified)
        # daily_vol = vol / sqrt(252)
        daily_vol = vol / np.sqrt(252)
        
        # Generate random daily returns
        # We need to simulate for 'days' number of days
        # For simplicity, let's assume a standard normal distribution for daily returns
        # and scale it by volatility.
        # A more accurate simulation would use the actual historical returns distribution,
        # but for this exercise, standard normal is acceptable.
        
        # Generate random shocks
        random_shocks = np.random.normal(0, 1, num_simulations)
        
        # Calculate price changes
        # Price_t = Price_0 * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
        # Assuming mu = 0 for simplicity in this calculation
        dt = 1/252 # Daily time step
        
        # Calculate final prices after 'days'
        # We can simplify this by calculating the total return over 'days'
        # Total return = N(0, days * daily_vol^2)
        
        # Let's use a simpler approach: simulate daily steps
        # Or even simpler: simulate the final price directly
        # Price_final = S * exp(-0.5 * vol^2 * T + vol * sqrt(T) * Z)
        # where T = days/252
        
        T = days / 252.0
        
        # Calculate final prices
        final_prices = S * np.exp(-0.5 * vol**2 * T + vol * np.sqrt(T) * random_shocks)
        
        # 3. Calculate VaR
        # VaR is the loss at a given confidence level
        # We sort the final prices and find the value at the percentile
        # Confidence level 0.95 means we are interested in the 5th percentile of losses
        # Or (1 - confidence_level) percentile of prices
        
        percentile = (1 - confidence_level) * 100
        var_price = np.percentile(final_prices, percentile)
        
        # VaR is usually expressed as a positive loss amount
        var_loss = S - var_price
        
        return float(var_loss)

    def get_current_price(self) -> float:
        """
        Returns the latest price from the injected historical data.
        """
        if self.historical_data is not None and not self.historical_data.empty:
            return float(self.historical_data['Close'].iloc[-1])
        return 0.0

    def calculate_historical_volatility(self) -> float:
        """
        Calculates the historical volatility based on returns. 
        Returns 0.0 if insufficient data.
        """
        if self.historical_data is None or self.historical_data.empty or len(self.historical_data) < 2:
            return 0.0
            
        close_prices = self.historical_data['Close']
        # Clean the data before math
        close_prices = close_prices.dropna()
        close_prices = close_prices[close_prices > 0]
        log_returns = np.log(close_prices / close_prices.shift(1))
        volatility = log_returns.std() * np.sqrt(252)
        return float(volatility)

class EuropeanOption(FinancialInstrument):
    """
    Represents a European-style option.
    """
    def __init__(self, ticker: str, strike_price: float, days_to_expiry: float, option_type: str = "call"):
        super().__init__(ticker)
        self.strike_price = strike_price
        self.days_to_expiry = days_to_expiry  # Time to expiry in years
        self.option_type = option_type.lower()
        self.sigma: Optional[float] = None # Implied or historical volatility

    def calculate_risk(self) -> float:
        """Placeholder for Delta/Gamma/Vega."""
        return 0.5

    def get_current_price(self, risk_free_rate: float = 0.05) -> float:
        """
        Calculates the theoretical price of the option using the Black-Scholes model.
        """
        # 1. Guard clause: We need data to get the current price and calculate volatility
        if self.historical_data is None or self.historical_data.empty or len(self.historical_data) < 2:
            return 0.0
            
        # 2. Extract S (Current Stock Price) and calculate T (Time in years)
        S = float(self.historical_data['Close'].iloc[-1])
        K = self.strike_price
        T = self.days_to_expiry / 365.0 
        
        # Handle expired options immediately
        if T <= 0:
            if self.option_type == 'call':
                return max(0.0, S - K)
            else:
                return max(0.0, K - S)

        # 3. Extract or Calculate Sigma (Volatility)
        if self.sigma is None:
            close_prices = self.historical_data['Close']
            log_returns = np.log(close_prices / close_prices.shift(1))
            self.sigma = float(log_returns.std() * np.sqrt(252))
            
        sigma = self.sigma
        r = risk_free_rate
        
        # 4. Black-Scholes Math implementation
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if self.option_type == "call":
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else: # put option
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
        return float(price)

    def calculate_option_price(ticker: str, strike_price: float, days_to_expiry: int, option_type: str) -> float:
        """Wrapper to calculate the theoretical price of an option."""
        raw_data = get_stock_prices(ticker, 365) # Need a year of data for volatility
        
        option = EuropeanOption(ticker, strike_price, days_to_expiry, option_type)
        option.load_historical_data(raw_data)
        
        return option.get_current_price()