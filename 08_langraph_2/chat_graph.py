from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver


class State(TypedDict):
    # messages are annotated and its a list and when ever we will assign it something it will add it into the message
    messages: Annotated[list, add_messages]

llm = init_chat_model(model_provider="google_genai", model="gemini-2.5-flash-lite", )

def chat_node(state: State):
    response = llm.invoke(state["messages"])
    # what ever we will return from here it will get appended to our list of messages because of Annotated.
    return {"messages": [response]}

graph_builder = StateGraph(State)

graph_builder.add_node("chat_node", chat_node)
graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)

graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer

def main():
    DB_URI = "mongodb://admin:password@localhost:27017"
    config = {"configurable":{"thread_id": "1"}}
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:

        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)

        query = input("> ")
        # this creates a ƒresh new state
        # result = graph.invoke({"messages": [{"role": "user", "content": query}]})
        result = graph_with_mongo.invoke({"messages": [{"role": "user", "content": query}]}, config)
        # and when the graph ends after invocation and completing its executions the state gets deleted
        print(result)  

main()