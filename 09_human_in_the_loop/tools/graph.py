from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
import requests
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

# by adding this decorator @tool() this became a tool according to langchain.
@tool()
def get_weather(city:str):
    # Api call to fetch the weather
    """This tool returns the weather data of the given city"""
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    
    return "Something went wrong!!!!!"

@tool()
def add_two_numbers(a:int, b:int):
    """this tool returns the sum of two numbers"""

    return a+b

tools = [get_weather,add_two_numbers]

class State(TypedDict):
    # messages are annotated and its a list and when ever we will assign it something it will add it into the message
    messages: Annotated[list, add_messages]

llm = init_chat_model(model_provider="groq", model="qwen/qwen3-32b")
llm_with_tools = llm.bind_tools(tools)

def chat_node(state: State):
    response = llm_with_tools.invoke(state["messages"])
    # what ever we will return from here it will get appended to our list of messages because of Annotated.
    return {"messages": [response]}

tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chat_node", chat_node)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "chat_node")

# if the chat_node's last message is a tool call then it will take the flow to tools_node
# so if the output is like this
# Tool Calls:
#   get_weather (f7b9c4b3-6110-457a-a3f6-50365ff3b610)
#  Call ID: f7b9c4b3-6110-457a-a3f6-50365ff3b610
#   Args:
#     city: delhi
# then this particular step make this possible that we pass this `f7b9c4b3-6110-457a-a3f6-50365ff3b610` id back and
# take this id to the tool_node and give back the result.
graph_builder.add_conditional_edges(
    "chat_node",
    tools_condition
)
graph_builder.add_edge("tools", "chat_node")

# this is how the flow will work
# start from the chat_node
# if there is not tool call needed for queries like hi hello etc..
# then end the procees 
# but if the last message is a tool call i.e. the last message needs an action then it will take it to tools_node
# tools_node is a executor node that will execute your tool in reality i.e. it will call your tool
# and after calling it will append the result from the tool into the messages array and return back to the chat_node 

graph = graph_builder.compile()

def main():

    query = input("> ")

    state = State(
        messages=[
            {
                "role":"user",
                "content": query
            }
        ]
    )

    for event in graph.stream(state, stream_mode="values"):
        if "messages" in event:
            event["messages"][-1].pretty_print()


main()