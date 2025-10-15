"""
Test cases for coding agent evaluation.
Organized by feature area for systematic testing.
"""

# File Operations Tests
FILE_OPERATIONS = [
    {
        "name": "create_simple_file",
        "input": "Create a hello.py file that prints 'Hello World'",
        "expected": {
            "files_created": ["hello.py"],
            "file_contains": {"hello.py": "print"},
            "success": True
        }
    },
    {
        "name": "read_existing_file",
        "input": "Read the contents of hello.py",
        "expected": {
            "mentions_content": True,
            "success": True
        }
    },
    {
        "name": "edit_file",
        "input": "Change 'Hello World' to 'Hello LangSmith!' in hello.py",
        "expected": {
            "files_modified": ["hello.py"],
            "file_contains": {"hello.py": "LangSmith"},
            "success": True
        }
    },
]

# Multi-file Project Tests
MULTI_FILE_PROJECTS = [
    {
        "name": "create_calculator_package",
        "input": """Create a calculator package with:
        - calculator/__init__.py
        - calculator/operations.py with add and subtract functions
        - calculator/tests.py with unit tests""",
        "expected": {
            "files_created": [
                "calculator/__init__.py",
                "calculator/operations.py", 
                "calculator/tests.py"
            ],
            "file_contains": {
                "calculator/operations.py": ["add", "subtract"],
                "calculator/tests.py": ["test_"]
            },
            "success": True
        }
    },
    {
        "name": "create_flask_app",
        "input": "Create a minimal Flask app with app.py and requirements.txt",
        "expected": {
            "files_created": ["app.py", "requirements.txt"],
            "file_contains": {
                "app.py": "Flask",
                "requirements.txt": "flask"
            },
            "success": True
        }
    },
]

# Contextual Awareness Tests
CONTEXTUAL_AWARENESS = [
    {
        "name": "multi_turn_file_reference",
        "conversations": [
            {
                "input": "Create a file called config.py with DEBUG=True",
                "expected": {"files_created": ["config.py"]}
            },
            {
                "input": "Add TESTING=False to that file",
                "expected": {
                    "references_previous": True,
                    "file_contains": {"config.py": ["DEBUG", "TESTING"]}
                }
            }
        ]
    },
    {
        "name": "remember_package_structure",
        "conversations": [
            {
                "input": "Create a utils package with string_utils.py",
                "expected": {"files_created": ["utils/string_utils.py"]}
            },
            {
                "input": "Add a function to capitalize text in the string utils module",
                "expected": {
                    "understands_context": True,
                    "files_modified": ["utils/string_utils.py"]
                }
            }
        ]
    },
]

# Git Integration Tests
GIT_OPERATIONS = [
    {
        "name": "git_status_check",
        "input": "Check the git status",
        "expected": {
            "uses_tool": "git_status",
            "success": True
        }
    },
    {
        "name": "create_branch",
        "input": "Create a new branch for a calculator feature",
        "expected": {
            "uses_tool": "git_create_branch",
            "branch_name_contains": "agent/",
            "success": True
        }
    },
    {
        "name": "git_workflow",
        "input": "Create a todo.py file with a TODO class, then commit it to a new branch",
        "expected": {
            "files_created": ["todo.py"],
            "uses_tools": ["git_create_branch", "git_stage_files", "git_commit"],
            "asks_before_push": True,
            "success": True
        }
    },
]

# Command Execution Tests
COMMAND_EXECUTION = [
    {
        "name": "run_python_script",
        "conversations": [
            {
                "input": "Create a script.py that prints the numbers 1 to 5",
                "expected": {"files_created": ["script.py"]}
            },
            {
                "input": "Run that script",
                "expected": {
                    "uses_tool": "run_command",
                    "output_contains": ["1", "2", "3", "4", "5"]
                }
            }
        ]
    },
    {
        "name": "install_and_test",
        "conversations": [
            {
                "input": "Create requirements.txt with requests library",
                "expected": {"files_created": ["requirements.txt"]}
            },
            {
                "input": "Install the requirements",
                "expected": {
                    "uses_tool": "run_command",
                    "command_contains": "pip install"
                }
            }
        ]
    },
]

# Error Handling Tests
ERROR_HANDLING = [
    {
        "name": "handle_file_not_found",
        "input": "Read a file called nonexistent_file.txt",
        "expected": {
            "success": False,
            "error_handled_gracefully": True,
            "mentions_file_not_found": True
        }
    },
    {
        "name": "handle_invalid_command",
        "input": "Run the command 'this_command_does_not_exist_xyz'",
        "expected": {
            "success": False,
            "error_handled_gracefully": True
        }
    },
]

# Complex Workflows
COMPLEX_WORKFLOWS = [
    {
        "name": "full_package_workflow",
        "conversations": [
            {
                "input": "Create a math_utils package with basic operations",
                "expected": {"files_created": ["math_utils/__init__.py", "math_utils/operations.py"]}
            },
            {
                "input": "Add tests for it",
                "expected": {"files_created": ["math_utils/tests.py"]}
            },
            {
                "input": "Run the tests",
                "expected": {"uses_tool": "run_command"}
            },
            {
                "input": "Commit everything to a new branch",
                "expected": {
                    "uses_tools": ["git_create_branch", "git_stage_files", "git_commit"]
                }
            }
        ]
    },
]

# All test cases combined
ALL_TEST_CASES = {
    "file_operations": FILE_OPERATIONS,
    "multi_file_projects": MULTI_FILE_PROJECTS,
    "contextual_awareness": CONTEXTUAL_AWARENESS,
    "git_operations": GIT_OPERATIONS,
    "command_execution": COMMAND_EXECUTION,
    "error_handling": ERROR_HANDLING,
    "complex_workflows": COMPLEX_WORKFLOWS,
}

def get_all_test_cases():
    """Get flattened list of all test cases."""
    cases = []
    for category, tests in ALL_TEST_CASES.items():
        for test in tests:
            test["category"] = category
            cases.append(test)
    return cases

def get_test_cases_by_category(category):
    """Get test cases for a specific category."""
    return ALL_TEST_CASES.get(category, [])

