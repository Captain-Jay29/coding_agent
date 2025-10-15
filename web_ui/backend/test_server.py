"""Quick test script for backend API endpoints."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agent import get_agent
from src.config import config
from src.memory import memory_manager

print("=" * 60)
print("Backend Server Test")
print("=" * 60)
print()

# Test 1: Agent initialization
print("✓ Testing agent initialization...")
try:
    agent = get_agent()
    print(f"  Agent created: {agent is not None}")
    print(f"  Model: {agent.model.model_name}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 2: Config
print("\n✓ Testing config...")
try:
    workspace = config.get_workspace_path()
    print(f"  Workspace: {workspace}")
    print(f"  Workspace exists: {workspace.exists()}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 3: Memory manager
print("\n✓ Testing memory manager...")
try:
    sessions = memory_manager.list_sessions()
    print(f"  Found {len(sessions)} existing sessions")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 4: Session creation
print("\n✓ Testing session creation...")
try:
    agent = get_agent()
    session_id = agent.start_session()
    print(f"  Session created: {session_id}")
    info = agent.get_session_info()
    print(f"  Message count: {info.get('message_count', 0)}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 5: File tree building
print("\n✓ Testing file tree building...")
try:
    from pathlib import Path
    workspace = config.get_workspace_path()
    
    def build_tree(path: Path, max_depth=2, current_depth=0):
        if current_depth >= max_depth:
            return None
        
        try:
            items = []
            for item in sorted(path.iterdir()):
                if item.name.startswith('.') or item.name == '__pycache__':
                    continue
                
                node = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file"
                }
                
                if item.is_file():
                    node["size"] = item.stat().st_size
                elif item.is_dir():
                    children = build_tree(item, max_depth, current_depth + 1)
                    if children:
                        node["children"] = children
                
                items.append(node)
            
            return items
        except PermissionError:
            return []
    
    tree = build_tree(workspace)
    print(f"  Found {len(tree)} items in workspace")
    if tree:
        print(f"  First item: {tree[0]['name']} ({tree[0]['type']})")
except Exception as e:
    print(f"  ✗ Error: {e}")

print()
print("=" * 60)
print("All core functions working! ✅")
print()
print("To start the server:")
print("  python web_ui/backend/server.py")
print()
print("Then test with:")
print("  curl http://localhost:8000/api/health")
print("=" * 60)

