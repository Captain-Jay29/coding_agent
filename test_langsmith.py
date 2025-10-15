"""
Quick test to verify LangSmith tracing is working.
Run this to see if traces appear in LangSmith dashboard.
"""

import os
from src.agent import get_agent
from src.config import config

def main():
    print("=" * 60)
    print("LangSmith Tracing Test")
    print("=" * 60)
    
    # Show configuration
    print("\nConfiguration:")
    print(f"  LangSmith Tracing: {config.get_langsmith_enabled()}")
    print(f"  LangSmith Project: {config.get_langsmith_project()}")
    print(f"  LangSmith API Key: {'Set' if config.get_langsmith_api_key() else 'Not set'}")
    print()
    
    if not config.get_langsmith_enabled():
        print("⚠️  LangSmith tracing is disabled!")
        print("To enable, set in your .env file:")
        print("  LANGCHAIN_TRACING_V2=true")
        print("  LANGCHAIN_API_KEY=<your-key>")
        print("  LANGCHAIN_PROJECT=coding-agent")
        return
    
    if not config.get_langsmith_api_key():
        print("❌ LangSmith API key not set!")
        print("Set LANGCHAIN_API_KEY in your .env file")
        return
    
    print("✅ LangSmith is configured!")
    print(f"\nCheck traces at: https://smith.langchain.com/o/your-org/projects/p/{config.get_langsmith_project()}")
    print()
    
    # Initialize agent
    print("Initializing agent...")
    agent = get_agent()
    
    # Test query
    test_query = "Create a hello.py file that prints 'Hello from LangSmith!'"
    print(f"\nTest query: {test_query}")
    print("\nProcessing...")
    print("-" * 60)
    
    try:
        response = agent.process_message(test_query)
        
        if response.get("success"):
            print("\n✅ Success!")
            print(f"\nAgent response:")
            print(response.get("response", "No response"))
            print("\n" + "=" * 60)
            print("🎉 Trace should now be visible in LangSmith!")
            print(f"Project: {config.get_langsmith_project()}")
            print("=" * 60)
        else:
            print(f"\n❌ Error: {response.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

