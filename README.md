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
   cd Tredence_task

2. Install dependencies:
   pip install -r requirements.txt

3. Start the server
   python run.py
   The server will start at http://127.0.0.1:8000.

## Testing the Workflow 

The easiest way to test the API is using the built-in Swagger UI. You don't need to use the terminal for requests.

**Step 1: Start the Workflow**
1.  Ensure the server is running (`python run.py`) and open your browser to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
2.  Click on the green **POST** bar labeled `/graph/run`.
3.  Click the **Try it out** button on the right.
4.  In the **Request body** box, paste the following JSON:
    ```json
    {
      "graph_id": "code_review_agent",
      "initial_state": {
        "raw_code": "def hello(): print(1)"
      }
    }
    ```
5.  Click the big blue **Execute** button.
6.  Scroll down to the **Server response** and copy the `run_id` (e.g., `"4a6feb1b-..."`).

**Step 2: Check the Results**
1.  Stay in the Swagger UI and scroll down to the blue **GET** bar labeled `/graph/state/{run_id}`.
2.  Click the **Try it out** button.
3.  Paste the `run_id` you copied earlier into the text box.
4.  Click the big blue **Execute** button.

**What you will see:**
In the response body, look for:
*   **"status"**: It should say `"completed"` (since the background task finished).
*   **"history"**: A list of steps showing the agent detecting issues, checking the score, and looping.
*   **"current_state"**: The final data (e.g., `complexity_score: 0`).


## Features and Capabilities 

1. Core Engine 

    1. Nodes: Standard Python functions that modify a shared state dictionary.
    2. State Management: State flows through nodes and is persisted to SQLite at every step.
    3. Branching & Looping: Supports add_conditional_edge to allow dynamic routing (e.g., looping back if quality checks fail).
    4. Async Execution: The engine runs asynchronously, allowing non-blocking I/O operations.

2. API And Architecture 

    1. FastAPI: Clean, typed REST endpoints with Pydantic validation.
    2. Background Tasks: Workflow execution happens in the background; the API returns a Run ID immediately.
    3. Persistence: Uses SQLite (via SQLAlchemy) to store execution history, allowing recovery of state even if the server restarts.
    4. WebSockets: Real-time log streaming for frontend observability.


## Future Improvements 

    Dynamic Graph DSL: Currently, graphs are defined in Python code. I would implement a JSON-based Domain Specific Language (DSL) so users can  define new workflows via an API call without restarting the server.

    Scalable Task Queue: Replace FastAPI BackgroundTasks with Celery or Redis Queue. This would allow the system to handle thousands of concurrent workflows and support retries for failed nodes.

    Visualization: Build a simple frontend using React Flow to visualize the execution path and state changes in real-time.

    Error Recovery: Add a "human-in-the-loop" feature where a workflow pauses on error and waits for manual API intervention to resume

    
