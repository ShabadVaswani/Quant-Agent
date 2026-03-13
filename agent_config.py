SYSTEM_PROMPT = """
You are a quantitative routing engine. 
Your primary objective is to answer questions about financial instruments.
You MUST NEVER guess or calculate math yourself. 
You MUST rely completely on the specific tools provided to you for any data retrieval or calculations.
IF USER ASKS COMPANY NAME INSTEAD OF TICKER SYMBOL, INTELLIGENTLY CONVERT IT TO TICKER SYMBOL IF COMMON KNOWLEDGE.
Round all the values to 2 decimal places.
"""
ROUTING_MODEL = "google/gemini-2.5-flash-lite"
SYNTHESIS_MODEL = "google/gemini-2.5-flash-lite"
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
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_option_price",
            "description": "Calculate the theoretical Black-Scholes price for a European call or put option.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "The underlying stock ticker (e.g., AAPL)."
                    },
                    "strike_price": {
                        "type": "number",
                        "description": "The strike price of the option."
                    },
                    "days_to_expiry": {
                        "type": "integer",
                        "description": "The number of days until the option expires."
                    },
                    "option_type": {
                        "type": "string",
                        "description": "The type of option: 'call' or 'put'.",
                        "enum": ["call", "put"]
                    }
                },
                "required": ["ticker", "strike_price", "days_to_expiry", "option_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_value_at_risk",
            "description": "Calculate the Value at Risk (VaR) for a stock using Monte Carlo simulation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "The stock ticker symbol (e.g., AAPL)."
                    },
                    "confidence_level": {
                        "type": "number",
                        "description": "The confidence level for VaR calculation (e.g., 0.95 for 95%).",
                        "default": 0.95
                    },
                    "days": {
                        "type": "integer",
                        "description": "The number of days into the future to simulate.",
                        "default": 1
                    },
                    "num_simulations": {
                        "type": "integer",
                        "description": "The number of Monte Carlo simulations to run.",
                        "default": 10000
                    }
                },
                "required": ["ticker"]
            }
        }
    }
]
