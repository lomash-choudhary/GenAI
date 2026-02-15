from fastapi import FastAPI, Query, Path
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
    # so now the enqueue will call process_query function with query as the parameter being sent to enqueue
    # and it returns us a job i.e. an id if it got enqueued or not

    job = queue.enqueue('rag_queue.queue.worker.process_query', query)
    return {
        "status": "queued",
        "job_id": job.id
    }


@app.get("/result/{job_id}")
def fetch_result(
    job_id: str = Path(..., description="Enter Job Id")
):
    job = queue.fetch_job(job_id=job_id)
    result = job.return_value()
    return {"result": result}
