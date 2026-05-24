import os
from dotenv import load_dotenv
from mem0 import Memory
from openai import OpenAI
import time
import json
load_dotenv()

HF_TOKEN=os.getenv("HF_TOKEN")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# you will have to create the configuration.

config = {
    "version": "v1.1",
    # "embedder":{
    #     "provider": "huggingface",
    #     "config":{
    #         "api_key": HF_TOKEN,
    #         "model":"sentence-transformers/all-MiniLM-L6-v2",
    #         "embedding_dims": 384
    #     }
    # },
    "embedder":{
        "provider": "gemini",
        "config":{
            "api_key": GEMINI_API_KEY,
            "model":"models/gemini-embedding-001",
            "embedding_dims": 384
        }
    },
    # "llm":{"provider": "groq", "config":{"api_key":GROQ_API_KEY, "model":"qwen/qwen3-32b"}},
    "llm":{"provider": "gemini", "config":{"api_key":GEMINI_API_KEY, "model":"gemini-2.5-flash-lite"}},
    "vector_store":{
        "provider":"qdrant",
        "config":{
            "host":"localhost",
            "port":6333,
            # unique collection every run
            "embedding_model_dims": 384
        }
    },
    "graph_store":{
        "provider":"neo4j",
        "config":{
            "url":"bolt://localhost:7687",
            "username":"neo4j",
            "password":"reform-william-center-vibrate-press-5829"
        }
    },
     "graph_memory": {
        "enabled": True
    }
}

mem_client = Memory.from_config(config)

def chat():
    while True:
        user_query = input("> ")

        # all_memories = mem_client.get_all(user_id="test") # by this we can get all the memory saved for the user `test` from the qdrant db.
        # but from the above approach the we can hit the context limits so thats why we will do the similarity search with the user query 

        relevant_memories = mem_client.search(query=user_query, filters={"user_id":"test"})

        # the results will be an array that will contain the data with hash id

        memories = [f"ID: {mem.get('id')} Memory: {mem.get('memory')}" for mem in relevant_memories.get("results")]

        # print("Memories", memories)


        SYSTEM_PROMPT= f"""
        You are are an memory aware assistant which response to user with context
        You are given with past memories and facts about the user

        Memory of the user:
        {json.dumps(memories)}
        """

        response_from_ai = client.chat.completions.create(
            model="gemini-2.5-flash-lite",
            messages=[
                    {"role":"system", "content": SYSTEM_PROMPT},
                    {"role":"user", "content": user_query}
                ]
        )   

        print(f"🤖: {response_from_ai.choices[0].message.content}")

        mem_client.add([
            {"role":"user", "content": user_query},
            {"role":"assistant", "content": response_from_ai.choices[0].message.content}
        ], user_id="test")

chat()