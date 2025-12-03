from email import contentmanager
import json
from pickletools import read_int4
from openai import OpenAI
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()


# Gemini API key client
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

#claude API Client
client_openAI = OpenAI(
    base_url="https://api.aimlapi.com/v1",
    api_key=os.getenv("API_KEY"),    
)


SYSTEM_PROMPT = """
    You are a helpful AI assistant specialized in resolving user queries through systematic analysis.

    Your process follows these exact steps in sequence:
    1. "analyse" - Break down and understand the user's input
    2. "think" - Process the information and plan your approach  
    3. "output" - Provide your direct response/solution
    4. "validate" - Self-check your output for accuracy and completeness
    5. "result" - Present the final, validated answer

    CRITICAL RULES:
    - Output ONLY ONE step at a time
    - Follow strict JSON format: {"step": "stepname", "content": "your_content"}
    - Never skip steps or combine them
    - Wait for external validation after "validate" step before proceeding
    - Be concise but thorough in each step
    - Stay focused on the user's actual question

    IDENTITY CONSISTENCY:
    - You are Gemini (Google's AI model)
    - Always maintain this identity throughout the conversation
    - If asked about your creator, respond that you were created by Google

    Example Flow:
    User: "What is 2 + 2?"
    Step 1: {"step": "analyse", "content": "User is asking for a basic arithmetic calculation: 2 + 2"}
    Step 2: {"step": "think", "content": "This is simple addition. I need to add 2 + 2 = 4"}
    Step 3: {"step": "output", "content": "4"}
    Step 4: {"step": "validate", "content": "The answer 4 is correct for 2 + 2"}
    [Wait for external validation]
    Step 5: {"step": "result", "content": "2 + 2 equals 4. This is calculated by adding the two numbers together."}
"""


user_message=[{"role":"system","content":SYSTEM_PROMPT}]


user_query = input("> ")


user_message.append(
        {"role":"user", "content":user_query}
    )

while True:
    
    response_from_ai = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={"type":"json_object"},
        messages=user_message
    )
    # we were able to do this i.e. directly append the content without using json because we are receiving the string from the response.
    user_message.append({"role":"assistant", "content":response_from_ai.choices[0].message.content})

    # we will get this response_from_ai in string format because responses are in string format so we need to parse them using json.loads
    parsed_response = json.loads(response_from_ai.choices[0].message.content)

    if parsed_response.get("step") != "result":
        print("     🧠", parsed_response.get("content"))
        continue

    elif parsed_response.get("step") == "result":
        print("\n\n 🤖:", parsed_response.get("content"), "\n\n")
        user_query = input("> ")

        user_message.append(
            {"role":"user", "content":user_query}
        )
        continue
    
    else:
        continue
