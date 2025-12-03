import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

#claude API Client
client = Anthropic(
    api_key=os.getenv("CLAUDE_API_KEY")
)

SYSTEM_PROMPT= """
    You are an helpful ai assistant which is specialized in resolving the user queries
    For the given user input, analyse the input and break down the problem step by step

    The steps are:
        You get a user input, 
        you analyse,
        you think,
        you think again,
        and think for several times and then return the output with an explaination.

    Follow the step in sequence that is "analyse", "think", "output", "validate" and finally "result".

    Rules:
        1. Follow the strict JSON output as per schema.
        2. Always perform one step at a time and wait for the next input.
        3. Carefully analyse the user query
        4. Always output only one JSON object at a time, strictly following { "step": "...", "content": "..." }.

    Output Format:
        {{"step": "string", "content": "string"}}

    
    Example:
        Input: what is 2 + 2
        Output: {{ "step" : "analyse", "content" : "Alright! The user is intereseted in maths query and he is asking as basic arithematic operation" }}
        Output: {{ "step" : "think", "content" : "To perform this operation i must go from left to right and add all the operands." }}
        Output: {{ "step" : "output", "content" : "4" }}
        Output: {{ "step" : "validate", "content" : "Seems like 4 is correct answer for 2+2" }}
        Output: {{ "step" : "result", "content" : "2+2 = 4 and that is calculated by adding all numbers" }}
"""


user_message=[]

user_query = input("> ")

user_message.append(
        {"role":"user", "content":user_query}
    )
while True:
    
    response_from_ai = client.messages.create(
        max_tokens=1024,
        messages=user_message,
        system=SYSTEM_PROMPT,
        model="claude-sonnet-4-20250514",
    )

    print("response from ai", response_from_ai)
    print("response from ai content", response_from_ai.content)


    # # we were able to do this i.e. directly append the content without using json because we are receiving the string from the response.
    # user_message.append({"role":"assistant", "content":response_from_ai.choices[0].message.content})

    # # we will get this response_from_ai in string format because responses are in string format so we need to parse them using json.loads
    # parsed_response = json.loads(response_from_ai.choices[0].message.content)

    # if parsed_response.get("step") != "result":
    #     print("     🧠", parsed_response.get("content"))
    #     continue

    # elif parsed_response.get("step") == "result":
    #     print("\n\n 🤖:", parsed_response.get("content"), "\n\n")
    #     user_query = input("> ")

    #     user_message.append(
    #         {"role":"user", "content":user_query}
    #     )
    #     continue
    
    # else:
    #     continue
