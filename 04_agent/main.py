from datetime import datetime
import json
import os
import string
import subprocess
from dotenv import load_dotenv
import requests
from openai import OpenAI
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def run_cmd(cmd:str):
    # this subprocess.run() runs a shell command in pyton
    result = subprocess.run(
        # shell=True tells the python to run it through shell like (bash or zsh)
        # capture_output=True this captures both standard output and error output instead of just printing them on terminal
        # text=True this decodes output from bytes -> string automatically.
        cmd, shell=True, capture_output=True, text=True
    )
    # after this command runs we get a CompletedProcess object (result) with
    # exit status (0 = success, non zero = error)
    # stdout -> text printed to standard output
    # stderr -> text printed to standard error
    
    '''
        {
            "exit_code": 0,
            "stdout":"File written successfully",
            "stderr": ""
        }

        {
            "exit_code": 1,
            "stdout":"",
            "stderr": "sh: syntax error near unexpected token"
        }
    '''
    

    return {
        "exit_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }

def get_weather(str:string):
    # Api call to fetch the weather

    url = f"https://wttr.in/{str}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {str} is {response.text}"
    
    return "Something went wrong!!!!!"

# SYSTEM_PROMPT = f"""
#     You are a helpfull assistant

#     Current date and time is {datetime.now()}
#     Current modinagars weather is -10 degree C.
# """

available_tools = {
    "get_weather": get_weather,
    "run_cmd": run_cmd
}

SYSTEM_PROMPT=f"""
    You are an helpfull assistant who is specialized in resolving user query.
    You work on start, plan, action, observer mode.

    for the given user query and available tools, plan the step by step execution, based on the planning, select the relevant tools from the available tools.
    and based on the tool selection you perform an action to call the tool

    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the output json format
    - Always perform one step at a time and wait for next input
    - Carefully analyze the user query.
    - Always output one JSON at a time.
    - Always output exactly one JSON object. No explanations, no code fences.

    Output:
    {{
        "step":"string",
        "content":"string",
        "function":"The name of function if the step is action",
        "input":"The input parameter for the function"
    }}

    Available Tools
    - "get_weather": Takes a city name as an input and returns the current weather of that city.
    - "run_cmd": Takes linux commands as a string and executes them and return the result of those commands after executing them.

    Example:
    User Query: What is the weather of New York?
    Output: {{ "step":"plan", "content":"The user is interested in the weather data of New York." }}
    Output: {{ "step":"plan", "content":"From the available tools call the get_weather tool" }}
    Output: {{ "step": "action", "function":"get_weather", "input":"new york" }}
    Output: {{ "step":"observe", "content":"12 Degree Celcius." }}
    Output: {{ "step":"output", "content":"the weather of new york seems to be 12 degrees" }}

"""


message_arr_for_ai = [{"role":"system", "content":SYSTEM_PROMPT}]

user_query = input("👨: ")

message_arr_for_ai.append({"role":"user", "content":user_query})

while True:
    response_from_ai = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={"type":"json_object"},
        messages=message_arr_for_ai
    )
    message_arr_for_ai.append({"role":"assistant", "content":response_from_ai.choices[0].message.content})

    # print(response_from_ai)

    try:
        parsed_response = json.loads(response_from_ai.choices[0].message.content)
    except json.JSONDecodeError as e:
        print("⚠️ JSON parse failed, raw content was:")
        print(response_from_ai.choices[0].message.content)
        continue  # or handle gracefully

    if parsed_response.get("step") == "plan":
        print(f"         🧠:   {parsed_response.get('content')}")
        continue
    elif parsed_response.get("step") == "action":
        tool_name = parsed_response.get("function")
        tool_input = parsed_response.get("input")

        print(f"🔨 : Calling tool {tool_name} with tool input {tool_input}")

        if(available_tools.get(tool_name)) != False:
            output = available_tools[tool_name](tool_input)
            message_arr_for_ai.append({"role":"user", "content": json.dumps({"step":"observer", "output":output})})
            continue
    elif parsed_response.get("step") == "output":
        print(f"  🤖: {parsed_response.get('content')}")

        user_query = input("> ")

        if(user_query) != "exit":
            message_arr_for_ai.append({"role":"user","content":user_query})
            continue
        else:
            break
    else:
        print(f" 🛞 {parsed_response.get('content')}")