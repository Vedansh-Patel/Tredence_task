import asyncio
import inspect
from typing import Dict, Any, Callable, Optional
from app.database import RunModel

END = "__END__"

class WorkflowGraph:
    def __init__(self):
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, Callable] = {}
        self.entry_point: str = ""

    def add_node(self, name: str, func: Callable):
        self.nodes[name] = func

    def set_entry_point(self, name: str):
        self.entry_point = name

    def add_edge(self, start_node: str, end_node: str):
        self.edges[start_node] = end_node

    def add_conditional_edge(self, start_node: str, condition_func: Callable):
        self.conditional_edges[start_node] = condition_func

    async def run(self, initial_state: Dict[str, Any], run_id: str, db_session, stream_callback: Optional[Callable] = None):
        """
        Executes the graph. 
        - Updates SQLite at every step for persistence.
        - Calls stream_callback for WebSocket updates.
        """
        current_node = self.entry_point
        state = initial_state.copy()
        step_count = 0
        history = []

        
        db_run = db_session.query(RunModel).filter(RunModel.run_id == run_id).first()
        if db_run:
            db_run.status = "running"
            db_session.commit()

        try:
            while current_node != END:
                step_count += 1
                
                
                if current_node not in self.nodes:
                    raise Exception(f"Node {current_node} not found")
                
                node_func = self.nodes[current_node]

                
                if inspect.iscoroutinefunction(node_func):
                    result = await node_func(state)
                else:
                    result = node_func(state)
                
                
                if isinstance(result, dict):
                    state.update(result)

                
                log_entry = {
                    "step": step_count,
                    "node": current_node,
                    "state": state.copy()
                }
                history.append(log_entry)

                
                if stream_callback:
                    await stream_callback(log_entry)

                
                db_run.state = state
                db_run.history = history
                db_session.commit()

                
                if current_node in self.conditional_edges:
                    next_node = self.conditional_edges[current_node](state)
                    current_node = next_node
                elif current_node in self.edges:
                    current_node = self.edges[current_node]
                else:
                    current_node = END

                
                await asyncio.sleep(0.5)

            
            db_run.status = "completed"
            db_session.commit()
            if stream_callback:
                await stream_callback({"status": "completed", "final_state": state})

        except Exception as e:
            print(f"Workflow Error: {e}")
            db_run.status = "failed"
            db_session.commit()
            if stream_callback:
                await stream_callback({"status": "failed", "error": str(e)})


