# Quant Agent

A quantitative routing engine that uses an LLM (via OpenRouter) and custom Python tools to answer financial questions, fetch market data, and perform calculations.

## Phase 1 Overview

This project implements an agentic loop where an LLM acts as the brain, routing user queries to specific, strictly typed Python tools. The agent is explicitly instructed *not* to guess or perform math itself, but rather to rely on its toolchain for accurate financial insights.

### Core Features
*   **Agentic Interaction Loop:** A continuous terminal interface where the user can ask financial questions.
*   **Tool Execution:** The LLM can dynamically select and execute multiple tools simultaneously based on the user's prompt.
*   **Object-Oriented Finance:** Financial instruments are modeled using OOP principles (e.g., the `Stock` subclass inheriting from an abstract `FinancialInstrument` class) allowing for scalable data injection and logic.
*   **Advanced Quantitative Models:** Implements actual statistical models, including historical log returns volatility, Black-Scholes for European option pricing, and Monte Carlo simulations for Value at Risk (VaR) calculations.
*   **Data Fetching:** Robust fetching of historical market data using `yfinance` and `pandas`.
*   **State Management:** The agent maintains conversation history and tool execution results, allowing for complex, multi-turn reasoning ("Second Hop" architecture).
*   **Safety Constraints:** Includes character limits on input to prevent context window exhaustion and error handling to ensure session stability during network or API failures.

## Project Structure

*   `main.py`: The entry point. Initializes the OpenAI client, manages the memory (`messages`), handles the interaction loop, tool dispatching, and execution.
*   `agent_config.py`: Contains the system prompt and JSON schema definitions for the tools available to the LLM.
*   `instruments.py`: Defines the foundational `FinancialInstrument` abstract base class and specific subclasses like `Stock` and `EuropeanOption`. Contains methods for calculating historical volatility, Black-Scholes option prices, and Monte Carlo Value at Risk (VaR).
*   `data_fetcher.py`: Contains functions for interacting with external APIs (like Yahoo Finance) to retrieve raw historical data.
*   `requirements.txt`: Lists all required Python packages.

## Prerequisites

*   Python 3.10+
*   An OpenRouter API Key.

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ShabadVaswani/Quant-Agent.git
    cd quant-agent
    ```

2.  **Set up the Virtual Environment:**
    ```bash
    python -m venv venv
    
    # On Windows:
    .\venv\Scripts\activate
    
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Create a `.env` file in the root directory.
    *   Add your OpenRouter API key:
        ```
        OPENROUTER_API_KEY="your_api_key_here"
        ```

## Usage

Run the main script from your terminal:

```bash
python main.py
```

You can then ask the agent questions such as:
*   *"What is the historical volatility of AAPL?"*
*   *"What is the 1-day Value at Risk for Google at a 99% confidence level?"*
*   *"Calculate the theoretical price for a call option on MSFT with a strike of 400 and 30 days to expiry."*

Type `quit` or `exit` to end the session.
