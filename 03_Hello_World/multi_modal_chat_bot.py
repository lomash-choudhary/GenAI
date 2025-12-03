import json
from openai import OpenAI
import os
from dotenv import load_dotenv


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


SYSTEM_PROMPT_OPENAI = """
    You are a validation AI that checks the accuracy and quality of another AI's responses.

    Your role is to:
    1. Review the previous AI's output against the original user query
    2. Validate whether the response correctly addresses the user's question
    3. Provide constructive feedback if improvements are needed
    4. Maintain objectivity and focus on accuracy

    VALIDATION RULES:
    - Output in JSON format: {"step": "openAIValidation", "content": "your_validation"}
    - Be concise but thorough in your validation
    - Focus on accuracy, relevance, and completeness
    - If the answer is correct, confirm it briefly
    - If improvements are needed, suggest specific changes
    - Don't repeat the original answer, just validate it

    VALIDATION CRITERIA:
    ✓ Does the output directly answer the user's question?
    ✓ Is the information factually correct?
    ✓ Is the response complete and helpful?
    ✓ Are there any logical errors or omissions?

    Example Validations:
    For correct answer: {"step": "openAIValidation", "content": "✓ Validated: The answer correctly solves 2+2=4 with proper mathematical reasoning."}

    For incorrect answer: {"step": "openAIValidation", "content": "⚠ Issue found: The calculation is incorrect. 2+2 should equal 4, not 5. Please recalculate."}

    For incomplete answer: {"step": "openAIValidation", "content": "⚠ Incomplete: The answer is correct but lacks explanation. Consider adding how the calculation was performed."}
"""

user_message=[{"role":"system","content":SYSTEM_PROMPT}]

user_message_for_openAI = [{"role":"system", "content":SYSTEM_PROMPT_OPENAI}]

user_query = input("> ")

user_message_for_openAI=[{"role":"user", "content":user_query}]

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
    user_message_for_openAI.append({"role":"assistant", "content":response_from_ai.choices[0].message.content})

    # we will get this response_from_ai in string format because responses are in string format so we need to parse them using json.loads
    parsed_response = json.loads(response_from_ai.choices[0].message.content)


    if parsed_response.get("step") == "validate":
        #call openAI api key
        user_message_for_openAI.append({"role":"assistant", "content":response_from_ai.choices[0].message.content})

        message_from_openAI = client_openAI.chat.completions.create(
            model="gpt-4o-mini",
            messages=user_message_for_openAI,
        )

        # print("\n\n\n message from open AI \n\n\n", message_from_openAI)
        # print("\n\n\n\nmessage from open AI choices [0] array kei andr ka .message 💦 \n\n\n", message_from_openAI.choices[0].message.content)

        user_message.append({"role":"assistant", "content":message_from_openAI.choices[0].message.content})
        user_message_for_openAI.append({"role":"assistant", "content":message_from_openAI.choices[0].message.content})

        print("      🔓AI", message_from_openAI.choices[0].message.content)
        continue

    elif parsed_response.get("step") != "result":
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
