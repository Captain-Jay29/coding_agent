"""
Execution Agent - LLM-based step execution.
Executes planned steps using tools.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate

# Import tools and config
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.tools import (
    write_file, read_file, run_command, list_directory,
    file_exists, get_file_info
)
from src.git_tools import GIT_TOOLS
from src.config import config
from ..state import PlanStep, ExecutionResult


class ExecutionAgent:
    """LLM-based agent that executes plan steps using tools."""
    
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
        
        # Collect all tools
        self.tools = [
            write_file,
            read_file, 
            run_command,
            list_directory,
            file_exists,
            get_file_info
        ] + GIT_TOOLS
        
        # Create agent executor
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an execution agent. Execute each step precisely as planned.

Your job:
1. Take the planned step and execute it using the appropriate tool
2. Handle any errors gracefully
3. Report results accurately

Context:
- All files are relative to workspace directory
- Commands run IN the workspace directory
- Git operations work with current repository"""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True
        )
    
    def execute_step(self, step: PlanStep) -> ExecutionResult:
        """Execute a single planned step."""
        try:
            # Format step as instruction
            instruction = f"""Execute step {step['step']}:
Action: {step['action']}
Arguments: {step['args']}
Description: {step.get('description', '')}

Use the {step['action']} tool with these exact arguments."""

            # Execute via agent
            result = self.agent_executor.invoke({"input": instruction})
            
            return {
                "step": step["step"],
                "success": True,
                "result": result.get("output", "Completed"),
                "error": None
            }
            
        except Exception as e:
            return {
                "step": step["step"],
                "success": False,
                "result": None,
                "error": str(e)
            }
    
    def execute_plan(self, plan: List[PlanStep]) -> tuple[List[ExecutionResult], List[str]]:
        """
        Execute complete plan step by step.
        
        Returns: (execution_results, files_modified)
        """
        execution_results = []
        files_modified = []
        
        for step in plan:
            result = self.execute_step(step)
            execution_results.append(result)
            
            # Track file modifications
            if result["success"] and step["action"] == "write_file":
                file_path = step["args"].get("file_path", "")
                if file_path:
                    files_modified.append(file_path)
            
            # Stop on critical errors
            if not result["success"] and step["action"] in ["write_file", "git_commit"]:
                break
        
        return execution_results, files_modified

