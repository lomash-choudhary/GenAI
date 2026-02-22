import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# this is our state that will store user query and the llm result for that particular query that llm result can be empty as well.
class State(TypedDict):
    query:str 
    llm_result: str | None

# then we create a node.
# a node is a simple function which will get or accept a state and return a state
def chat_bot(state: State):
    # in this function we can do anything suppose we called OpenAI for the user query
    query = state['query']
    # message_arr_for_ai.append({"role":"user", "content": query})

    #llm call (query)
    response_from_ai = client.chat.completions.create(
        model="gemini-2.5-flash",
        # response_format={"type":"json_object"},
        # messages=message_arr_for_ai
        messages=[ 
            {
                "role":"user",
                "content":query
            }
        ]
    )

    # message_arr_for_ai.append({"role":"assistant", "content": response_from_ai.choices[0].message.content})

    result = response_from_ai.choices[0].message.content

    # then we will update the state

    state['llm_result'] = result
    return {
        "query": query,
        "llm_result": result
    }

# from this StateGraph we will create a graph and we will pass our state to the graph.
# this is graph builder, we will have to tell this graph that we want to add a node to this graph
graph_builder = StateGraph(State)

# we have added the chat_bot node into the graph builder.
graph_builder.add_node("chat_bot", chat_bot)

# graph builder will take us from start to the chat bot node
graph_builder.add_edge(START, "chat_bot")
# and then graph builder will take us from chat bot to the end
graph_builder.add_edge("chat_bot", END)


# in the end we will compile this graph builder i.e. we will build this graph.
graph = graph_builder.compile()

def main():
    user = input("> ")


    _state = {
        "query": user,
        "llm_result": None
    }

    # invoke the graph
    # this invoke needs a state
    graph_result = graph.invoke(_state)

    print("Graph Result", graph_result)

main()
