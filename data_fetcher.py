import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_prices(ticker_symbol: str, days: int) -> pd.DataFrame:
    """
    Download historical price data for a given ticker over a specify number of days.
    """
    stock = yf.Ticker(ticker_symbol)
    
    # Calculate reliable date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates as strings for yfinance compatibility
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    try:
        # Fetch data using explicit dates
        data = stock.history(start=start_str, end=end_str)
        
        if data.empty:
            return pd.DataFrame(columns=['Close'])
            
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return pd.DataFrame(columns=['Close'])

if __name__ == "__main__":
    print("Testing with valid ticker 'AAPL':")
    valid_data = get_stock_prices("AAPL", 5)
    print(valid_data)
    
    print("\nTesting with fake ticker 'FAKE123':")
    fake_data = get_stock_prices("FAKE123", 5)
    print(fake_data)
