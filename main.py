import os
import json
from agent_config import SYSTEM_PROMPT, tools
from openai import OpenAI
from dotenv import load_dotenv

# Import our custom modules
from data_fetcher import get_stock_prices
from instruments import Stock

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


# Initialize messages list (agent memory)
messages = []

# Add system prompt as the first message
messages.append({"role": "system", "content": SYSTEM_PROMPT})

def calculate_historical_volatility(ticker: str) -> float:
    """
    Wrapper function to calculate volatility using the Stock class.
    """
    stock = Stock(ticker)
    return stock.calculate_historical_volatility()

# Tool Registry
available_functions = {
    "get_stock_prices": get_stock_prices,
    "calculate_historical_volatility": calculate_historical_volatility,
}

# Main agent interaction loop
print("Quant Agent initialized. Type 'quit' or 'exit' to end the session.")

while True:
    user_input = input("\nAsk the Quant Agent: ")
    
    # Edge Case 1: Handle empty input
    if not user_input.strip():
        continue
        
    if len(user_input) > 1000:
        print("[WARNING] Input is too long. Please keep it under 1000 characters.")
        continue
        
    if user_input.lower() in ['quit', 'exit']:
        print("Goodbye!")
        break
    
    messages.append({"role": "user", "content": user_input})
    
    # Edge Case 2: Handle API/Network errors
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-001", 
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
    except Exception as e:
        print(f"\n[ERROR] Connection issue: {e}")
        # Remove the failed user message so it doesn't corrupt future state
        messages.pop() 
        continue

    response_message = response.choices[0].message
    messages.append(response_message.model_dump(exclude_none=True))
    
    # Branching Logic: Check if the agent wants to call a tool
    if response_message.tool_calls:
        print(f"\n[SYSTEM] Agent is executing {len(response_message.tool_calls)} tool(s)...")
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            tool_call_id = tool_call.id
            
            # 1. Parse Arguments
            try:
                function_args = json.loads(tool_call.function.arguments)
            except Exception as e:
                print(f"[ERROR] Failed to parse arguments for {function_name}: {e}")
                continue
            
            # 2. Fetch Function
            function_to_call = available_functions.get(function_name)
            
            # 3. Execute & Convert to String
            if function_to_call:
                try:
                    print(f"[SYSTEM] Executing {function_name}({function_args})...")
                    function_response = function_to_call(**function_args)
                    tool_result = str(function_response)
                except Exception as e:
                    tool_result = f"Error executing {function_name}: {e}"
            else:
                tool_result = f"Error: Function {function_name} not found."
            
            print(f"[DEBUG] Result from {function_name}: {tool_result[:100]}...")
            
            # 4. Update memory with tool result
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": function_name,
                "content": tool_result
            })
            
        # 5. Second Hop: Get final answer from LLM
        try:
            second_response = client.chat.completions.create(
                model="google/gemini-2.0-flash-001",
                messages=messages
            )
            final_message = second_response.choices[0].message
            print(f"\nQuant Agent: {final_message.content}")
            # Append final message to memory
            messages.append(final_message.model_dump(exclude_none=True))
        except Exception as e:
            print(f"\n[ERROR] Final response failed: {e}")
            
    else:
        # If no tool calls, just print the AI's verbal response
        print(f"\nQuant Agent: {response_message.content}")