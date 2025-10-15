"""
Run evaluations on the coding agent using LangSmith.
Tests the agent against the evaluation dataset and reports results.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langsmith import Client
from langsmith.evaluation import evaluate
from src.agent import get_agent
from src.config import config
from evals.evaluators import run_all_evaluators, calculate_overall_score


def agent_function(inputs: dict) -> dict:
    """Wrapper function to run agent for evaluation."""
    agent = get_agent()
    
    try:
        user_input = inputs.get("input", "")
        response = agent.process_message(user_input)
        
        return {
            "response": response.get("response", ""),
            "success": response.get("success", False),
            "error": response.get("error"),
            "metadata": response.get("metadata", {})
        }
    except Exception as e:
        return {
            "response": str(e),
            "success": False,
            "error": str(e),
            "metadata": {}
        }


def custom_evaluator(run, example):
    """Custom evaluator that uses our evaluation functions."""
    outputs = run.outputs or {}
    expected = example.outputs or {}
    
    # Run all evaluators
    eval_results = run_all_evaluators(outputs, expected)
    
    # Calculate overall score
    overall_score = calculate_overall_score(eval_results)
    
    # Format results for LangSmith
    return {
        "key": "overall",
        "score": overall_score,
        "results": eval_results
    }


def main():
    print("=" * 60)
    print("LangSmith Evaluation Runner")
    print("=" * 60)
    print()
    
    # Check configuration
    if not config.get_langsmith_api_key():
        print("❌ LangSmith API key not set!")
        print("Set LANGCHAIN_API_KEY in your .env file")
        return
    
    print("✅ Configuration valid")
    print(f"   Project: {config.get_langsmith_project()}")
    print()
    
    # Initialize client
    client = Client(
        api_key=config.get_langsmith_api_key(),
        api_url=config.langsmith_endpoint
    )
    
    # Get dataset
    dataset_name = "coding-agent-eval-suite"
    print(f"Loading dataset: {dataset_name}")
    
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
        examples_count = len(list(client.list_examples(dataset_id=dataset.id)))
        print(f"✅ Found {examples_count} test cases")
        print()
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        print("\nCreate the dataset first by running:")
        print("  python evals/create_langsmith_dataset.py")
        return
    
    # Run evaluation
    print("🚀 Starting evaluation...")
    print("This may take a few minutes depending on dataset size.")
    print("-" * 60)
    
    try:
        results = evaluate(
            agent_function,
            data=dataset_name,
            evaluators=[custom_evaluator],
            experiment_prefix="coding-agent-eval",
            max_concurrency=1,  # Run one at a time to avoid rate limits
        )
        
        print()
        print("=" * 60)
        print("📊 Evaluation Complete!")
        print("=" * 60)
        print()
        print(f"Results summary:")
        print(f"  View detailed results at:")
        print(f"  https://smith.langchain.com/o/your-org/projects/p/{config.get_langsmith_project()}")
        print()
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

