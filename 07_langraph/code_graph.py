import os
from typing_extensions import TypedDict
from typing import Literal
from langgraph.graph import StateGraph, START, END
from openai import OpenAI, chat
from dotenv import load_dotenv
from pydantic import BaseModel
# pydantic is a validation model, so what we did is we passed this pydantic model in our api call, so that we are able to tell our chat model that the response which you will give us should be in 
# this format ClassifyMessageResponse

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
# we created this class by passingg BaseModel into it, so that we are able to send this structure to the api call.
class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool

# we will use structured response for the accuracy as well

class AccuracyMessageResponse(BaseModel):
    accuracy_percentage: str

# we created our state.
class State(TypedDict):
    user_query: str
    llm_result: str | None
    accuracy_percentage: str | None
    is_coding_question: bool | None

# then we will create our nodes
# 1. classify_query

def classify_query(state: State):
    query = state['user_query']
    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to detect if the user's query is related to coding or not i.e. if the user query is a coding question or not.
    Return the response in the specified JSON boolean only.
    """

    # Structured Outputs / Responses -> for this we will use python lib called pydantic -> similar to zod in JS.

    # we want to get the boolean value for the user query so we need to control the output of this for this we will learn about structured responses.
    response = client.chat.completions.parse(
        model="gemini-2.5-flash-lite",
        response_format=ClassifyMessageResponse,
        messages=[
            {
                "role":"system",
                "content":SYSTEM_PROMPT
            },
            {
                "role":"user",
                "content": query
            }
        ]
    )

    is_coding_question = response.choices[0].message.parsed.is_coding_question
    state['is_coding_question'] = is_coding_question
    return state

# next we will write our routing node.
# from routing we will have to return a literal i.e. a list
# coz langraph needs to know before hand where we can route our queries, so we will just prvoide those nodes name in the list
def route_query(state: State) -> Literal["general_query_resolver", "coding_query_resolver"]:
    is_coding_question = state["is_coding_question"]
    if is_coding_question:
        return "coding_query_resolver"
    
    return "general_query_resolver"

# node 2 -> general query resolved

def general_query_resolver(state: State):
    query = state["user_query"]

    response = client.chat.completions.create(
        model="gemini-2.5-flash-lite",
        messages=[
            {
                "role" : "user",
                "content": query
            }
        ]
    )

    result = response.choices[0].message.content

    state["llm_result"] = result

    return state

# node 3 -> for solving coding queries.
def coding_query_resolver(state: State):
    query = state["user_query"]

    SYSTEM_PROMPT="""
    You are an helpful assistant you will receive the user's coding query you have to solve that coding query in the best possible manner to the user.
    """

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {
                "role" : "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role":"user",
                "content":query
            }
        ]
    )

    result = response.choices[0].message.content

    state["llm_result"] = result

    return state

# node 4 -> coding query validator
def coding_query_validator(state: State):
    query = state['user_query']
    llm_response = state["llm_result"]

    SYSTEM_PROMPT = f"""
    You are expert in calculating accracy of the code according to the user query.
    Return the percentage of accuracy.
    User Query: {query}
    llm_response: {llm_response}
    """

    response = client.chat.completions.parse(
        model="gemini-2.5-flash-lite",
        response_format=AccuracyMessageResponse,
        messages=[
            {
                "role":"system",
                "content":SYSTEM_PROMPT
            },
            {
                "role":"user",
                "content": query
            },
            {
                "role":"assistant",
                "content":llm_response
            }
        ]
    )

    result = response.choices[0].message.content

    state['accuracy_percentage'] = result

    return state



graph_builder = StateGraph(State)

# Define nodes
graph_builder.add_node("classify_query", classify_query)
# since route query is also a type of node so we will also add a node of this.
graph_builder.add_node("route_query", route_query)
graph_builder.add_node("general_query_resolver", general_query_resolver)
graph_builder.add_node("coding_query_resolver", coding_query_resolver)
graph_builder.add_node("coding_query_validator", coding_query_validator)

# Define edges

graph_builder.add_edge(START, "classify_query")

# then we will add a conditional edge.
graph_builder.add_conditional_edges("classify_query", route_query, {
    "general_query_resolver": "general_query_resolver",
    "coding_query_resolver": "coding_query_resolver"
})

# if you ended up into the general query then next you will go to end
graph_builder.add_edge("general_query_resolver", END)

# but if you entered into the coding query then you will have to go to validator
graph_builder.add_edge("coding_query_resolver", "coding_query_validator")
# and then after the coding_query_validator you will go to end.
graph_builder.add_edge("coding_query_validator", END)


graph = graph_builder.compile()

def main():
    user_query = input("> ")

    _state: State = {
        "user_query": user_query,
        "llm_result": None,
        "accuracy_percentage": None,
        "is_coding_question": False
    }

    graph_result = graph.invoke(_state)

    print("graph_result\n\n\n", graph_result)

main()
