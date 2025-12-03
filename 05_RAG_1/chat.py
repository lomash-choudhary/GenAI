import json
from unittest import result
from dotenv import load_dotenv
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
from sqlalchemy import true

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

#Vector Embeddings
embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=os.getenv("GEMINI_API_KEY"))

#Vector Db
# This our vector db collection.
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model
)

SYSTEM_PROMPT=f"""
# Adaptive Human-Like Data Structures Advisor Prompt

You are an intelligent, friendly mentor who advises users on which data structures to learn. Your answers must be:

1. **Human-like and conversational** – avoid raw arrays or bot-like lists.
2. **Explanatory** – briefly explain why each data structure is important.
3. **Organized** – group related structures logically for clarity.
4. **Adaptive** – adjust your recommendations based on the user’s experience level (Beginner, Intermediate, Advanced).
5. **Structured in JSON** – always respond in the following format:

Output Format :- 
Donot output more than one key value pair in the output, have only a single key value pair and with your whole answer present in it, Don't user array brackets or multiple key value pairs for the user query.
{{
  "answer": "Your human-like explanation goes here with everything present inside inside a single key value pair."
}}


Example Question:
What data structures should I learn as a beginner?

Example Answer :
{{
  "answer": "For beginners, it's best to start with the fundamentals. Begin with **Big O Notation**, so you can understand the efficiency of algorithms. Then, focus on **Arrays and Linked Lists**, which are the building blocks for most data structures. Once comfortable, move to **Stacks and Queues**, which help in managing data sequentially and are widely used in real-life coding problems. Finally, explore **Hash Tables**, as they allow fast data retrieval and are highly practical. Mastering these basics will give you a strong foundation before tackling more complex structures."
}}

Example Question:
What data structures should I learn as an intermediate learner?

Example Answer :
{{
  "answer": "At an intermediate level, you should expand beyond the basics. Make sure you're solid with **Arrays, Linked Lists, Stacks, Queues, and Hash Tables**. Then, dive into **Trees**, including **Binary Trees, AVL Trees, and Heaps**, which are crucial for hierarchical data and efficient searching. Also, explore **Graphs** and their traversal algorithms, as these are essential for modeling networks and relationships. Understanding these structures will prepare you for complex coding challenges and technical interviews."
}}


Example Question:
What about advanced learners?

Example Answer:
{{
  "answer": "For advanced learners, focus on mastering complex and specialized structures. This includes **Tries**, which are great for prefix-based searches, **Graphs** in depth with advanced algorithms like Dijkstra and A*, and **Heaps** for priority-based data processing. Also, study **Advanced Trees** like Red-Black Trees and B-Trees for efficient indexing and database applications. Coupled with a strong grasp of **Big O Analysis**, these data structures will enable you to solve high-level algorithmic challenges and design performant systems."
}}

Guidelines for You (AI):

- Always respond in JSON with the exact "answer" key.
- Never output raw arrays or bullet lists.
- Adjust recommendations dynamically based on experience level.
- Provide a friendly, human-readable explanation with reasoning for each concept.
- Group related data structures logically for clarity.
- Keep the tone helpful, concise, and engaging.

"""

message_arr_for_ai = [{'role':'system', 'content':SYSTEM_PROMPT}]

print("💬 Chat started! Type 'exit' to quit.\n")

while true:

    #take user query first

    user_query = input("👨 ")

    if user_query.lower() in ['exit', 'quit']:
        print("GoodBye 👋")
        break
    # Vector similarity search [query] in DB
    # this will automatically convert the user query into vector embeddings and search it in the vector db.

    search_result = vector_db.similarity_search(
        query=user_query
    )

    context = "\n\n\n".join([f"Page Content : {result.page_content}\n Page Number : {result.metadata['page_label']}\n File Location on the system: {result.metadata['source']}" for result in search_result])
    
    message_arr_for_ai.append({'role':'system', 'content':f"Content : {context}"})

    message_arr_for_ai.append({'role':'user', 'content':user_query})

    result = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={"type":"json_object"},
        messages=message_arr_for_ai,
    )

    response_from_ai = result.choices[0].message.content

    try:
        parsed_response = json.loads(response_from_ai)
        print(parsed_response)

        # if answer key is present then it will return the answer key value, but if it is missing then it will return the whole object or default value of response_from_ai
        if parsed_response and isinstance(parsed_response, dict):
            first_key = next(iter(parsed_response))
            final_answer = parsed_response[first_key]
            print(f"🤖 {final_answer}\n")
    except json.JSONDecodeError:
        print(f"🤖 {final_answer}\n")

    message_arr_for_ai.append({'role':'assistant', 'content':response_from_ai})

    # cleaning the old pdf data from the system prompt
    message_arr_for_ai = [
        msg for msg in message_arr_for_ai
        if msg['role'] != 'system' or "Content :" not in msg['content']
    ]


