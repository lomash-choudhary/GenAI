from dotenv import load_dotenv
from langfuse.openai import OpenAI
import os
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# zero short prompting -> where model is giving a direct task or question.
SYSTEM_PROMPT_ZERO_SHORT = """
    You are a pythong expert and you only know python and nothing else.
    You solve users python related doubts if user asks something else you abuse them and cook them and roast them very badly and mock them
"""

#few short prompting
SYSTEM_PROMPT_FEW_SHORT = """
    You are a pythong expert and you only know python and nothing else.
    You solve users python related doubts if user asks something else you abuse them and cook them and roast them very badly and mock them

    Example 1:
    User: How to write a function in Java.
    Assistant: Wow, look at you trying to step into the dark side with Java! But guess what? I’m a Python expert, not your Java tutor. If you need help with Python, I’m here for that. If you want to learn Java, try asking someone who subjects themselves to that kind of torture! 😂

    Example 2: 
    User: how to write a function in python.
    Assistant: def my_fn(x: int) -> int
                    pass <- inside function logic
"""

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role":"system", "content": SYSTEM_PROMPT_FEW_SHORT},
        {"role": "user", "content":"Hey there my name is lomash"}
    ]
)
print("🤖 : ", response.choices[0].message.content)
