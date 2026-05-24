from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import interrupt, Command
import json

@tool()
def human_assistance(query:str)->str:
    """Request assistance from human."""
    human_response = interrupt({"query": query}) # this saves the state in db and kills the graph i.e. the last state in the db will be the query which the user asked
    return human_response["data"]

tools = [human_assistance]

class State(TypedDict):
    # messages are annotated and its a list and when ever we will assign it something it will add it into the message
    messages: Annotated[list, add_messages]

llm = init_chat_model(model_provider="groq", model="qwen/qwen3-32b")
llm_with_tools = llm.bind_tools(tools=tools)

def chatbot(state:State):
    message = llm_with_tools.invoke(state['messages'])
    return {"messages": [message]}


tool_node = ToolNode(tools=tools)
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)


def user_chat():
    DB_URI = "mongodb://admin:password@localhost:27017"
    config = {"configurable":{"thread_id": "6"}}
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = create_chat_graph(mongo_checkpointer)
        while True:

            query = input("> ")

            state = State(
                messages=[
                    {
                        "role":"user",
                        "content":query
                    }
                ]
            )
            for event in graph_with_mongo.stream(state, config, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()
    

def admin_call():
    DB_URI = "mongodb://admin:password@localhost:27017"
    config = {"configurable":{"thread_id": "6"}}
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = create_chat_graph(mongo_checkpointer)

        state = graph_with_mongo.get_state(config=config)
        last_message = state.values["messages"][-1] # we first fetch the last message from the DB to get to know what was the last message

        tool_calls = last_message.additional_kwargs.get("tool_calls",[]) # then we are checking if that last message was a tool call or not?

        user_query = None

        for call in tool_calls:
            if call.get("function", {}).get("name") == "human_assistance": # if we got a tool call by name `human_assistance` then we will get the arguments for that particular tool call and save those arguments in the user_query
                args = call["function"].get("arguments", "{}")
                try:
                    args_dict = json.loads(args)
                    user_query = args_dict.get("query")
                except json.JSONDecodeError:
                    print("Failed to decode function arguments.")

        print("User has a query", user_query) # show to the admin that the user has a query and ask for the solution and then resume back the graph.

        solution = input("> ")

        resume_command = Command(resume={"data":solution}) # this resume_command will resume the graph.

        # now start streaming the graph again

        for event in graph_with_mongo.stream(resume_command, config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()


# admin_call()
user_chat()