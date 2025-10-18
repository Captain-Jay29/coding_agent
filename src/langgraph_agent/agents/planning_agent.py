"""
Planning Agent - LLM-based plan generation.
Breaks down user requests into executable steps.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Import config
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.config import config
from ..state import PlanStep


class PlanningAgent:
    """LLM-based agent that creates execution plans."""
    
    def __init__(self, model_name: str = None, temperature: float = None):
        # Use config values if not provided
        model_config = config.get_model_config()
        model_name = model_name or model_config["model_name"]
        temperature = temperature if temperature is not None else model_config["temperature"]
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=config.get_openai_api_key()
        )
    
    def create_plan(self, user_input: str, context: Dict[str, Any] = None) -> List[PlanStep]:
        """
        Generate execution plan from user input.
        
        Returns structured plan with steps, actions, and args.
        """
        system_prompt = """You are a planning agent. Break down user requests into atomic, executable steps.

Available tools:
- write_file: Create/overwrite files. Args: {file_path: str, content: str}
- read_file: Read file contents. Args: {file_path: str}
- run_command: Execute shell command. Args: {command: str}
- list_directory: List directory contents. Args: {directory_path: str}
- git_create_branch: Create git branch. Args: {branch_name: str}
- git_commit: Commit changes. Args: {message: str}
- git_stage_files: Stage files. Args: {files: List[str]} or {} for all

Output format (JSON array):
[
  {
    "step": 1,
    "action": "write_file",
    "args": {"file_path": "app.py", "content": "print('hello')"},
    "description": "Create app.py with hello world"
  },
  {
    "step": 2,
    "action": "run_command",
    "args": {"command": "python app.py"},
    "description": "Run the script"
  }
]

Rules:
1. Keep steps atomic and sequential
2. Check dependencies (e.g., install before run)
3. Use correct tool arguments
4. Be specific with file paths
5. Use conversation history to understand context and references
6. Return ONLY valid JSON array"""

        # Start with system message
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history for context
        if context and context.get("messages"):
            messages.extend(context["messages"])
        
        # Add current request
        user_prompt = f"""Create execution plan for:

Request: {user_input}

Return JSON array of steps:"""
        messages.append(HumanMessage(content=user_prompt))
        
        try:
            response = self.llm.invoke(messages)
            plan_text = response.content.strip()
            
            # Extract JSON from markdown code blocks if present
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_text:
                plan_text = plan_text.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(plan_text)
            
            # Validate plan structure
            validated_plan = []
            for item in plan:
                validated_plan.append({
                    "step": item.get("step", len(validated_plan) + 1),
                    "action": item["action"],
                    "args": item["args"],
                    "description": item.get("description", "")
                })
            
            return validated_plan
            
        except Exception as e:
            # Fallback: simple single-step plan
            return [{
                "step": 1,
                "action": "run_command",
                "args": {"command": f"echo 'Planning failed: {str(e)}'"},
                "description": f"Fallback action: {user_input}"
            }]

