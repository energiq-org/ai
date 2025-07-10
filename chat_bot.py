import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from helpers.tools_sql_helper import *
from helpers.chat_history_helper import *

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def chat_bot(user_id: str, user_input: str) -> str:
    append_message(user_id, "user", user_input)

    messages = get_history(user_id)
    if not any(m["role"] == "system" for m in messages):
        messages.insert(0, {"role": "system", "content": instructions})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools_sql,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    available_functions = {
        "getMonthlySpending": getMonthlySpending,
        "getAvgTransactionAmount": getAvgTransactionAmount,
        "getMaxTransactions": getMaxTransactions,
        "getMonthlyEnergyUsage": getMonthlyEnergyUsage,
        "getMonthlyEnergyPerVehicle": getMonthlyEnergyPerVehicle,
        "getAvgSessionDurationPerVehicle": getAvgSessionDurationPerVehicle,
        "getMostFrequentChargingWeekdays": getMostFrequentChargingWeekdays,
        "getMonthlyUsageTrends": getMonthlyUsageTrends,
        "getMostEfficientMonth": getMostEfficientMonth,
        "getAvgSessionStats": getAvgSessionStats,
        "reserveSession": reserveSession,
        "retrieveEVKnowledge": retrieveEVKnowledge
    }

    if tool_calls:
        assistant_tool_msg = {
            "role": response_message.role,
            "content": None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        }
        append_message(user_id, response_message.role, assistant_tool_msg)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            function_args["user_id"] = user_id
            
            function_response = function_to_call(**function_args)

            tool_msg = {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response),
            }
            append_message(user_id, "tool", tool_msg)

        messages = get_history(user_id)

        final_response = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=tools_sql, tool_choice="none"
        )

        assistant_final = final_response.choices[0].message
        append_message(user_id, "assistant", assistant_final.content)

        return assistant_final.content

    else:
        # No tool used, just direct assistant response
        append_message(user_id, "assistant", response_message.content)
        return response_message.content
    
    
if __name__ == "__main__":
    # Set your actual user ID
    user_id = "73f52a4b-fd1b-4119-9233-ff8a956f5512"

    # New user input
    user_input = f"""what is the average transaction for the last 4 months"""
    print(chat_bot(user_id, user_input))