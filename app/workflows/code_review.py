import random
from typing import Dict, Any
from app.core.engine import WorkflowGraph, END



def extract_code(state: Dict[str, Any]):
    print("-> Extracting code...")
    code = state.get("raw_code", "")
    return {"lines": len(code.split("\n")), "complexity_score": 0}

def check_complexity(state: Dict[str, Any]):
    print("-> Checking complexity...")
    
    current = state.get("complexity_score", 0)
    if current == 0:
        score = random.randint(10, 20) 
    else:
        score = current 
    return {"complexity_score": score}

def detect_issues(state: Dict[str, Any]):
    print("-> Detecting issues...")
    issues = state.get("issues", [])
    issues.append(f"Issue found at step {random.randint(1, 100)}")
    return {"issues": issues}

def suggest_improvements(state: Dict[str, Any]):
    print("-> Suggesting improvements (Refactoring)...")
    
    current_score = state.get("complexity_score", 10)
    new_score = max(0, current_score - 5) 
    return {"complexity_score": new_score}



def quality_gate(state: Dict[str, Any]):
    score = state.get("complexity_score", 100)
    print(f"   [Gate] Complexity: {score}")
    
    if score > 5:
        return "suggest_improvements" 
    return END 



def create_code_review_workflow() -> WorkflowGraph:
    workflow = WorkflowGraph()
    
    workflow.add_node("extract", extract_code)
    workflow.add_node("complexity", check_complexity)
    workflow.add_node("detect_issues", detect_issues)
    workflow.add_node("suggest_improvements", suggest_improvements)
    
    workflow.set_entry_point("extract")
    
    workflow.add_edge("extract", "complexity")
    workflow.add_edge("complexity", "detect_issues")
    
    
    workflow.add_conditional_edge("detect_issues", quality_gate)
    workflow.add_edge("suggest_improvements", "complexity")
    
    return workflow


