# Mini Agent Workflow Engine

A lightweight, backend-only workflow engine built with **FastAPI** and **Python**. This system allows you to define nodes, edges, and conditional logic to build stateful AI agents.

It includes a working implementation of a **Code Review Agent** that mimics a loop of "Extract -> Check Complexity -> Detect Issues -> Refactor" until quality thresholds are met.

## How to Run

### Prerequisites
* Python 3.9+

### Installation
1. Clone the repository:
   ```bash
   git clone <YOUR_REPO_URL>
   cd ai-workflow-engine

2. Install dependencies:
   pip install -r requirements.txt

3. Start the server
   python run.py
   The server will start at http://127.0.0.1:8000.

## Testing the Workflow 

1. You can use the automated Swagger UI at http://127.0.0.1:8000/docs or curl.

2. Trigger a Run:
   curl -X POST "http://127.0.0.1:8000/graph/run" \
     -H "Content-Type: application/json" \
     -d '{
           "graph_id": "code_review_agent",
           "initial_state": {
             "raw_code": "def complex_function(): ... "
           }
         }'

3. Check Status: 
   Use the run_id returned from the previous step
   curl -X GET "http://127.0.0.1:8000/graph/state/{YOUR_RUN_ID}"

4. Real time Streaming: 
   Connect via WebSocket to see logs as they happen:
   ws://127.0.0.1:8000/ws/logs/{YOUR_RUN_ID}

## Features and Capabilities 

1. Core Engine 

    -> Nodes: Standard Python functions that modify a shared state dictionary.
    -> State Management: State flows through nodes and is persisted to SQLite at every step.
    -> Branching & Looping: Supports add_conditional_edge to allow dynamic routing (e.g., looping back if quality checks fail).
    -> Async Execution: The engine runs asynchronously, allowing non-blocking I/O operations.

2. API And Architecture 

    -> FastAPI: Clean, typed REST endpoints with Pydantic validation.
    -> Background Tasks: Workflow execution happens in the background; the API returns a Run ID immediately.
    -> Persistence: Uses SQLite (via SQLAlchemy) to store execution history, allowing recovery of state even if the server restarts.
    -> WebSockets: Real-time log streaming for frontend observability.


## Future Improvements 

    -> Dynamic Graph DSL: Currently, graphs are defined in Python code. I would implement a JSON-based Domain Specific Language (DSL) so users can define new workflows via an API call without restarting the server.
    -> Scalable Task Queue: Replace FastAPI BackgroundTasks with Celery or Redis Queue. This would allow the system to handle thousands of concurrent workflows and support retries for failed nodes.
    -> Visualization: Build a simple frontend using React Flow to visualize the execution path and state changes in real-time.
    -> Error Recovery: Add a "human-in-the-loop" feature where a workflow pauses on error and waits for manual API intervention to resume