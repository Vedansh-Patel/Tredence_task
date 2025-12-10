from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class GraphCreationRequest(BaseModel):
    name: str
    description: str = "A workflow graph"

class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

class GraphRunResponse(BaseModel):
    run_id: str
    status: str

class RunStatusResponse(BaseModel):
    run_id: str
    graph_id: str
    status: str
    current_state: Dict[str, Any]
    history: List[Dict[str, Any]]


    