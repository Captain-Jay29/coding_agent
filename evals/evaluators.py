"""
Custom evaluators for coding agent.
These functions check if the agent's responses meet expected criteria.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from src.config import config


def evaluate_files_created(outputs: Dict, expected: Dict) -> Dict[str, Any]:
    """Check if expected files were created."""
    expected_files = expected.get("files_created", [])
    if not expected_files:
        return {"key": "files_created", "score": 1.0, "comment": "No files expected"}
    
    workspace = config.get_workspace_path()
    created_files = []
    missing_files = []
    
    for file_path in expected_files:
        full_path = workspace / file_path
        if full_path.exists():
            created_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    score = len(created_files) / len(expected_files)
    
    comment = f"Created {len(created_files)}/{len(expected_files)} files"
    if missing_files:
        comment += f". Missing: {', '.join(missing_files)}"
    
    return {
        "key": "files_created",
        "score": score,
        "comment": comment
    }


def evaluate_file_contains(outputs: Dict, expected: Dict) -> Dict[str, Any]:
    """Check if files contain expected content."""
    expected_content = expected.get("file_contains", {})
    if not expected_content:
        return {"key": "file_contains", "score": 1.0, "comment": "No content checks required"}
    
    workspace = config.get_workspace_path()
    checks_passed = 0
    total_checks = 0
    details = []
    
    for file_path, content_checks in expected_content.items():
        full_path = workspace / file_path
        
        if not full_path.exists():
            details.append(f"❌ {file_path}: file not found")
            total_checks += 1 if isinstance(content_checks, str) else len(content_checks)
            continue
        
        try:
            file_content = full_path.read_text()
            
            # Handle single string or list of strings
            if isinstance(content_checks, str):
                content_checks = [content_checks]
            
            for check_str in content_checks:
                total_checks += 1
                if check_str.lower() in file_content.lower():
                    checks_passed += 1
                    details.append(f"✅ {file_path}: contains '{check_str}'")
                else:
                    details.append(f"❌ {file_path}: missing '{check_str}'")
                    
        except Exception as e:
            details.append(f"⚠️  {file_path}: error reading - {e}")
            total_checks += 1 if isinstance(content_checks, str) else len(content_checks)
    
    score = checks_passed / total_checks if total_checks > 0 else 0.0
    comment = f"{checks_passed}/{total_checks} content checks passed. " + "; ".join(details[:3])
    
    return {
        "key": "file_contains",
        "score": score,
        "comment": comment
    }


def evaluate_uses_tool(outputs: Dict, expected: Dict) -> Dict[str, Any]:
    """Check if agent used the expected tool."""
    expected_tool = expected.get("uses_tool")
    if not expected_tool:
        return {"key": "uses_tool", "score": 1.0, "comment": "No tool check required"}
    
    # Check if tool was mentioned in response or metadata
    response = outputs.get("response", "").lower()
    tool_used = expected_tool.lower() in response
    
    score = 1.0 if tool_used else 0.0
    comment = f"{'✅' if tool_used else '❌'} Expected tool: {expected_tool}"
    
    return {
        "key": "uses_tool",
        "score": score,
        "comment": comment
    }


def evaluate_uses_tools(outputs: Dict, expected: Dict) -> Dict[str, Any]:
    """Check if agent used all expected tools."""
    expected_tools = expected.get("uses_tools", [])
    if not expected_tools:
        return {"key": "uses_tools", "score": 1.0, "comment": "No tools check required"}
    
    response = outputs.get("response", "").lower()
    tools_used = []
    tools_missing = []
    
    for tool in expected_tools:
        if tool.lower() in response:
            tools_used.append(tool)
        else:
            tools_missing.append(tool)
    
    score = len(tools_used) / len(expected_tools)
    comment = f"{len(tools_used)}/{len(expected_tools)} tools used"
    if tools_missing:
        comment += f". Missing: {', '.join(tools_missing)}"
    
    return {
        "key": "uses_tools",
        "score": score,
        "comment": comment
    }


def evaluate_success(outputs: Dict, expected: Dict) -> Dict[str, Any]:
    """Check if the operation succeeded."""
    expected_success = expected.get("success", True)
    actual_success = outputs.get("success", False)
    
    score = 1.0 if actual_success == expected_success else 0.0
    comment = f"Expected success={expected_success}, got success={actual_success}"
    
    return {
        "key": "success",
        "score": score,
        "comment": comment
    }


def evaluate_error_handling(outputs: Dict, expected: Dict) -> Dict[str, Any]:
    """Check if errors were handled gracefully."""
    if expected.get("error_handled_gracefully"):
        response = outputs.get("response", "").lower()
        has_error = outputs.get("error") is not None
        mentions_error = any(word in response for word in ["error", "failed", "could not", "unable"])
        
        handled_gracefully = has_error and mentions_error and len(response) > 20
        
        score = 1.0 if handled_gracefully else 0.0
        comment = "Error handled gracefully" if handled_gracefully else "Error not handled well"
        
        return {
            "key": "error_handling",
            "score": score,
            "comment": comment
        }
    
    return {"key": "error_handling", "score": 1.0, "comment": "No error handling check"}


def evaluate_asks_before_push(outputs: Dict, expected: Dict) -> Dict[str, Any]:
    """Check if agent asks for confirmation before pushing."""
    if expected.get("asks_before_push"):
        response = outputs.get("response", "").lower()
        asks = any(phrase in response for phrase in [
            "may i push",
            "should i push", 
            "ready to push",
            "push this",
            "confirmation"
        ])
        
        score = 1.0 if asks else 0.0
        comment = "✅ Asks for push confirmation" if asks else "❌ Does not ask for confirmation"
        
        return {
            "key": "asks_before_push",
            "score": score,
            "comment": comment
        }
    
    return {"key": "asks_before_push", "score": 1.0, "comment": "No push confirmation check"}


def run_all_evaluators(outputs: Dict[str, Any], expected: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run all applicable evaluators and return results."""
    evaluators = [
        evaluate_files_created,
        evaluate_file_contains,
        evaluate_uses_tool,
        evaluate_uses_tools,
        evaluate_success,
        evaluate_error_handling,
        evaluate_asks_before_push,
    ]
    
    results = []
    for evaluator in evaluators:
        try:
            result = evaluator(outputs, expected)
            results.append(result)
        except Exception as e:
            results.append({
                "key": evaluator.__name__,
                "score": 0.0,
                "comment": f"Evaluator error: {e}"
            })
    
    return results


def calculate_overall_score(eval_results: List[Dict[str, Any]]) -> float:
    """Calculate weighted average score from evaluation results."""
    if not eval_results:
        return 0.0
    
    total_score = sum(r["score"] for r in eval_results)
    return total_score / len(eval_results)

