import json
import os
from openai import OpenAI
from pydantic import conint
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    # andi mandi sandi jisne api key churai uski 
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
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

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role":"user", "content":"Hello my name is lomash"},
        # json.dumps change a python object into a JSON Formatted string.
        {"role":"assistant", "content":json.dumps({
            "step": "analyse",
            "content": "The user has introduced themselves by stating their name is 'lomash'. This is a simple greeting and self-introduction."
        })},
        {"role":"assistant", "content":json.dumps({
            "step": "think", "content": "The user has provided their name. As an AI assistant, I should acknowledge this introduction and prepare a polite greeting that references their name, setting a welcoming tone for further interaction. This doesn't involve complex computation, but rather social interaction."
        })},
        {"role":"assistant", "content":json.dumps({
            "step": "output",
            "content": "Hello Lomash! It's nice to meet you. How can I assist you today?"
        })},
        {"role":"assistant", "content":json.dumps({
            "step": "validate", "content": "The output 'Hello Lomash! It's nice to meet you. How can I assist you today?' correctly acknowledges the user's name and prompts for their next query, which is appropriate for an initial interaction."
        })},
    ]
)

print(response.choices[0].message.content)
