# Standard library imports
import json
import shutil
from datetime import datetime

# Third-party imports
from openai import OpenAI

from Python_tool.PythonExecutor_secure import execute_python_code as run_python_code
from web_tool.web_browsing import text_search as search_web
from wiki_tool.search_wiki import fetch_wikipedia_content as search_wiki


client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
MODEL = "lmstudio-community/qwen2.5-7b-instruct"

Tools = [{
    "type": "function",
    "function": {
        "name": "run_python_code",
        "description": "Execute Python code and return the execution results. Use for math problems or task automation.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Complete Python code to execute. Must return a value."}
            },
            "required": ["code"]
        }
    }
}]

def process_stream(stream, add_assistant_label=True):
    """Handle streaming responses from the API"""
    collected_text = ""
    tool_calls = []
    first_chunk = True

    for chunk in stream:
        delta = chunk.choices[0].delta

        # Handle regular text output
        if delta.content:
            if first_chunk:
                print()
                if add_assistant_label:
                    print("Assistant:", end=" ", flush=True)
                first_chunk = False
            print(delta.content, end="", flush=True)
            collected_text += delta.content

        # Handle tool calls
        elif delta.tool_calls:
            for tc in delta.tool_calls:
                if len(tool_calls) <= tc.index:
                    tool_calls.append({
                        "id": "", "type": "function",
                        "function": {"name": "", "arguments": ""}
                    })
                tool_calls[tc.index] = {
                    "id": (tool_calls[tc.index]["id"] + (tc.id or "")),
                    "type": "function",
                    "function": {
                        "name": (tool_calls[tc.index]["function"]["name"] + (tc.function.name or "")),
                        "arguments": (tool_calls[tc.index]["function"]["arguments"] + (tc.function.arguments or ""))
                    }
                }
    return collected_text, tool_calls

def chat_loop():
    messages = []
    print("Assistant: What can I help you with?")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "quit":
            break

        messages.append({"role": "user", "content": user_input})
        continue_tool_execution = True

        while continue_tool_execution:
            # Get response
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=Tools,
                stream=True,
                temperature=0.2
            )
            response_text, tool_calls = process_stream(response)

            if not tool_calls:
                print()
                continue_tool_execution = False

            text_in_response = len(response_text) > 0
            if text_in_response:
                messages.append({"role": "assistant", "content": response_text})

            # Handle tool calls if any
            if tool_calls:
                tool_name = tool_calls[0]["function"]["name"]
                print()
                if not text_in_response:
                    print("Assistant:", end=" ", flush=True)
                print(f"Calling Tool: {tool_name}")
                messages.append({"role": "assistant", "tool_calls": tool_calls})

                # Execute tool calls
                for tool_call in tool_calls:
                    arguments = json.loads(tool_call["function"]["arguments"])

                    if tool_call["function"]["name"] == "run_python_code":
                        result = run_python_code(arguments["code"])
                        messages.append({
                            "role": "tool",
                            "content": str(result),
                            "tool_call_id": tool_call["id"]
                        })
                        terminal_width = shutil.get_terminal_size().columns
                        print("\n" + "-" * terminal_width)
                        print(arguments["code"])
                        print("-" * terminal_width)
                        if result["success"]:
                            if result["output"]:
                                print(f"Output:\n{result['output']}")
                            if result["result"] is not None:
                                print(f"Result:\n{result['result']}")
                        else:
                            print(f"Error running and executing the code\n{result['error']}")
                        print("-" * terminal_width)

                # Continue checking for more tool calls after tool execution
                continue_tool_execution = True
            else:
                continue_tool_execution = False

if __name__ == "__main__":
    chat_loop()