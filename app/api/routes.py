import uuid
import json
import asyncio
from typing import List

from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.schemas import GraphRunRequest, GraphRunResponse, RunStatusResponse, GraphCreationRequest
from app.database import get_db, RunModel
from app.workflows.code_review import create_code_review_workflow
from app.database import SessionLocal

router = APIRouter()


graphs = {
    "code_review_agent": create_code_review_workflow()
}


class ConnectionManager:
    def __init__(self):
        
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, run_id: str):
        await websocket.accept()
        if run_id not in self.active_connections:
            self.active_connections[run_id] = []
        self.active_connections[run_id].append(websocket)

    def disconnect(self, websocket: WebSocket, run_id: str):
        if run_id in self.active_connections:
            self.active_connections[run_id].remove(websocket)
            if not self.active_connections[run_id]:
                del self.active_connections[run_id]

    async def send_log(self, run_id: str, message: dict):
        if run_id in self.active_connections:
            
            for connection in self.active_connections[run_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    
                    pass

manager = ConnectionManager()


async def background_workflow_runner(graph_id: str, run_id: str, initial_state: dict):
    """
    Runs the workflow in the background. 
    Creates its own DB session to avoid thread conflicts.
    """
    db = SessionLocal()
    workflow = graphs[graph_id]
    
    async def ws_callback(log_data):
        await manager.send_log(run_id, log_data)
    
    try:
        await workflow.run(initial_state, run_id, db, ws_callback)
    finally:
        db.close()



@router.post("/graph/create")
def create_graph(payload: GraphCreationRequest):
   
    return {"message": "Graph blueprint registered", "graph_id": "code_review_agent"}

@router.post("/graph/run", response_model=GraphRunResponse)
def run_graph(
    payload: GraphRunRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    if payload.graph_id not in graphs:
        raise HTTPException(status_code=404, detail="Graph not found")

    run_id = str(uuid.uuid4())

    
    new_run = RunModel(
        run_id=run_id,
        graph_id=payload.graph_id,
        state=payload.initial_state,
        status="pending"
    )
    db.add(new_run)
    db.commit()

    
    background_tasks.add_task(
        background_workflow_runner, 
        payload.graph_id, 
        run_id, 
        payload.initial_state
    )

    return GraphRunResponse(run_id=run_id, status="pending")

@router.get("/graph/state/{run_id}", response_model=RunStatusResponse)
def get_run_state(run_id: str, db: Session = Depends(get_db)):
    run = db.query(RunModel).filter(RunModel.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return RunStatusResponse(
        run_id=run.run_id,
        graph_id=run.graph_id,
        status=run.status,
        current_state=run.state,
        history=run.history
    )



@router.websocket("/ws/logs/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await manager.connect(websocket, run_id)
    try:
        while True:
            
            await websocket.receive_text() 
    except WebSocketDisconnect:
        manager.disconnect(websocket, run_id)


