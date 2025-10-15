# Evaluation Framework

Systematic testing and evaluation of the coding agent using LangSmith.

## 📁 Structure

```
evals/
├── datasets/
│   └── test_cases.py          # Test case definitions
├── create_langsmith_dataset.py # Upload test cases to LangSmith
├── evaluators.py               # Custom evaluation functions
├── run_evals.py                # Main evaluation runner
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Ensure LangSmith is configured

Make sure your `.env` file has:
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your-key>
LANGCHAIN_PROJECT=coding-agent
```

### 2. Create the dataset

```bash
cd /Users/jay/Desktop/coding_agent
source venv/bin/activate
python evals/create_langsmith_dataset.py
```

This uploads all test cases to LangSmith.

### 3. Run evaluations

```bash
python evals/run_evals.py
```

This runs the agent against all test cases and reports results.

## 📊 Test Categories

### File Operations (3 tests)
- Create simple file
- Read existing file
- Edit file content

### Multi-file Projects (2 tests)
- Create calculator package
- Create Flask app

### Contextual Awareness (2 tests)
- Multi-turn file reference
- Remember package structure

### Git Operations (3 tests)
- Check git status
- Create branch
- Full git workflow (create, commit, ask to push)

### Command Execution (2 tests)
- Run Python scripts
- Install and test packages

### Error Handling (2 tests)
- Handle file not found
- Handle invalid commands

### Complex Workflows (1 test)
- Full package creation, testing, and git workflow

**Total: ~20 test cases** covering all major features

## 🔍 Evaluators

Custom evaluators check:

| Evaluator | Checks |
|-----------|--------|
| `evaluate_files_created` | Expected files exist in workspace |
| `evaluate_file_contains` | Files contain expected content/code |
| `evaluate_uses_tool` | Agent used specific tool |
| `evaluate_uses_tools` | Agent used all required tools |
| `evaluate_success` | Operation succeeded/failed as expected |
| `evaluate_error_handling` | Errors handled gracefully |
| `evaluate_asks_before_push` | Git push requires confirmation |

## 📈 Viewing Results

After running evaluations:

1. Go to https://smith.langchain.com/
2. Navigate to your project (coding-agent)
3. Look for experiments starting with "coding-agent-eval-"
4. View:
   - Overall pass rate
   - Individual test results
   - Detailed traces
   - Performance metrics

## 🛠️ Adding New Tests

### 1. Add to `datasets/test_cases.py`

```python
NEW_CATEGORY = [
    {
        "name": "test_name",
        "input": "User query to test",
        "expected": {
            "files_created": ["file.py"],
            "success": True
        }
    }
]

# Add to ALL_TEST_CASES
ALL_TEST_CASES["new_category"] = NEW_CATEGORY
```

### 2. Update dataset

```bash
python evals/create_langsmith_dataset.py
```

### 3. Run new evaluations

```bash
python evals/run_evals.py
```

## 🎯 Best Practices

### When to Run Evals

- ✅ Before merging major changes
- ✅ After adding new features
- ✅ When fixing bugs (add regression test)
- ✅ Weekly as part of CI/CD

### Interpreting Results

| Score | Meaning | Action |
|-------|---------|--------|
| 90-100% | Excellent | Ship it! |
| 70-89% | Good | Investigate failures |
| 50-69% | Needs work | Debug issues |
| <50% | Broken | Fix before deploying |

### Debugging Failed Tests

1. Click on failed test in LangSmith
2. View full trace
3. See exactly what the agent did
4. Check tool calls and responses
5. Fix the issue
6. Re-run evaluations

## 🔄 Continuous Improvement

### Workflow

```
1. Add new test case for feature/bug
2. Run eval (expect failure)
3. Fix agent code
4. Run eval again
5. Iterate until passing
6. Commit changes
```

### Tracking Progress

LangSmith automatically tracks:
- Score trends over time
- Which tests fail most often
- Performance regressions
- Improvement over iterations

## 🐛 Troubleshooting

### "Dataset not found"
```bash
# Create it first
python evals/create_langsmith_dataset.py
```

### "API key error"
Check your `.env` file has `LANGCHAIN_API_KEY` set correctly.

### "Import errors"
Make sure you're in the project root and venv is activated:
```bash
cd /Users/jay/Desktop/coding_agent
source venv/bin/activate
```

### "Tests timing out"
Reduce concurrency in `run_evals.py`:
```python
max_concurrency=1  # Run one test at a time
```

## 📚 Resources

- [LangSmith Docs](https://docs.smith.langchain.com/)
- [Evaluation Guide](https://docs.smith.langchain.com/evaluation)
- [Custom Evaluators](https://docs.smith.langchain.com/evaluation/custom-evaluators)

