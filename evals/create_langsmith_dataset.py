"""
Upload evaluation test cases to LangSmith.
Creates a dataset that can be used for systematic agent evaluation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langsmith import Client
from evals.datasets.test_cases import get_all_test_cases
from src.config import config

def create_dataset():
    """Create LangSmith dataset from test cases."""
    
    # Check configuration
    if not config.get_langsmith_api_key():
        print("❌ LangSmith API key not set!")
        print("Set LANGCHAIN_API_KEY in your .env file")
        return
    
    # Initialize client
    client = Client(
        api_key=config.get_langsmith_api_key(),
        api_url=config.langsmith_endpoint
    )
    
    dataset_name = "coding-agent-eval-suite"
    
    print(f"Creating dataset: {dataset_name}")
    print("=" * 60)
    
    # Create or get dataset
    try:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Comprehensive test suite for coding agent - file ops, git, context, and workflows"
        )
        print(f"✅ Created new dataset: {dataset.name}")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"📋 Dataset already exists, fetching it...")
            dataset = client.read_dataset(dataset_name=dataset_name)
        else:
            raise e
    
    print(f"Dataset ID: {dataset.id}")
    print()
    
    # Get test cases
    test_cases = get_all_test_cases()
    print(f"Loading {len(test_cases)} test cases...")
    print()
    
    # Upload examples
    added_count = 0
    for test_case in test_cases:
        try:
            # Handle single-turn tests
            if "input" in test_case:
                example_input = {
                    "input": test_case["input"],
                    "category": test_case.get("category", "unknown")
                }
                example_output = test_case.get("expected", {})
                
                client.create_example(
                    dataset_id=dataset.id,
                    inputs=example_input,
                    outputs=example_output,
                    metadata={
                        "test_name": test_case.get("name", "unnamed"),
                        "category": test_case.get("category", "unknown")
                    }
                )
                added_count += 1
                print(f"  ✅ {test_case['category']}/{test_case['name']}")
            
            # Handle multi-turn conversations
            elif "conversations" in test_case:
                for idx, turn in enumerate(test_case["conversations"]):
                    example_input = {
                        "input": turn["input"],
                        "category": test_case.get("category", "unknown"),
                        "conversation_turn": idx + 1,
                        "total_turns": len(test_case["conversations"])
                    }
                    example_output = turn.get("expected", {})
                    
                    client.create_example(
                        dataset_id=dataset.id,
                        inputs=example_input,
                        outputs=example_output,
                        metadata={
                            "test_name": f"{test_case['name']}_turn_{idx+1}",
                            "category": test_case.get("category", "unknown"),
                            "is_multi_turn": True
                        }
                    )
                    added_count += 1
                print(f"  ✅ {test_case['category']}/{test_case['name']} ({len(test_case['conversations'])} turns)")
                
        except Exception as e:
            print(f"  ⚠️  Failed to add {test_case.get('name', 'unknown')}: {e}")
    
    print()
    print("=" * 60)
    print(f"🎉 Dataset creation complete!")
    print(f"   Added: {added_count} examples")
    print(f"   Dataset: {dataset_name}")
    print(f"   View at: https://smith.langchain.com/o/your-org/datasets/{dataset.id}")
    print("=" * 60)

if __name__ == "__main__":
    create_dataset()

