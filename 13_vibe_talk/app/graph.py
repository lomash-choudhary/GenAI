import subprocess
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
@tool
def run_command(cmd:str):
    """
    Takes a command line prompt and executes it on the user's machine and retunrs the output of the command
    Example: run_command(cmd="ls") where ls is the command to list the files.
    """
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    return result.stdout if result.stdout else result.stderr

available_tools = [run_command]

llm = init_chat_model(model_provider="google_genai", model="gemini-3.1-flash-lite")
llm_with_tool = llm.bind_tools(tools=available_tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chat_bot(state:State):
    SYSTEM_PROMPT = SystemMessage(content="""
        You are an AI Coding assistant who takes an input from user and based on available tools you choose 
        the correct tool and execute the commands.
                                  
        You can even execute commands and help user with the output of the command
                                  
        Always make sure to keep your generated code and files in vibe_coding/ folder. You can create one
        if not already there.
    """)

    generate_message = llm_with_tool.invoke([SYSTEM_PROMPT] + state["messages"])
    return { "messages": generate_message }


tool_node = ToolNode(tools=available_tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chat_bot", chat_bot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chat_bot")
graph_builder.add_conditional_edges(
    "chat_bot",
    tools_condition
)
graph_builder.add_edge("tools", "chat_bot")
graph_builder.add_edge("chat_bot", END)

graph = graph_builder.compile()