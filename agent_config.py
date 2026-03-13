SYSTEM_PROMPT = """
You are a quantitative routing engine. 
Your primary objective is to answer questions about financial instruments.
You MUST NEVER guess or calculate math yourself. 
You MUST rely completely on the specific tools provided to you for any data retrieval or calculations.
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_prices",
            "description": "Fetch historical market data for a given ticker and number of days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker_symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol (e.g., AAPL)."
                    },
                    "days": {
                        "type": "integer",
                        "description": "The number of days of historical data to fetch."
                    }
                },
                "required": ["ticker_symbol", "days"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_historical_volatility",
            "description": "Calculate the historical risk/volatility of a specific stock ticker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "The stock ticker symbol to calculate volatility for."
                    }
                },
                "required": ["ticker"]
            }
        }
    }
]
