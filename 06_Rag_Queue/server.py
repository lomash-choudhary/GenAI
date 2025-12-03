from fastapi import FastAPI, Query
from .queue.connection import queue

app = FastAPI()

@app.get("/server")
def server():
    return {
        "message": "Server is up and running on port 8000"
    }

@app.post("/chat")
def chat(
    query: str = Query(..., description="Enter your query")
):
    # in this route we have to take user query, pass it to the queue and notify the user that their query has been queued

    pass