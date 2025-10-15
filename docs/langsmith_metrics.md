# LangSmith Metrics & Tagging

## 📊 What's Being Tracked

### Automatic Tags (Applied to Every Trace)

**Task Type Tags:**
- `git-operation` - Git commands (commit, push, branch, pull)
- `file-creation` - Creating new files
- `file-reading` - Reading/viewing files
- `file-editing` - Modifying existing files
- `command-execution` - Running shell commands
- `package-management` - Installing dependencies

**Complexity Tags:**
- `simple-query` - Short, straightforward requests
- `complex-query` - Long or multi-part requests

**Success Tags:**
- `success` - Operation completed successfully
- `error` - Operation failed
- `error-{ErrorType}` - Specific error type (e.g., `error-RuntimeError`)

**Performance Tags:**
- `fast` - Completed in < 3 seconds
- `slow` - Took > 10 seconds

**Conversation Tags:**
- `single-turn` - First message in session
- `multi-turn` - Part of ongoing conversation

**Tool Usage Tags:**
- `no-tools` - Agent responded without using any tools
- `single-tool` - Agent used exactly one tool
- `multi-tool` - Agent used multiple tools (2+)

---

## 📈 Metadata Tracked

Every trace includes:

| Metric | Type | Description |
|--------|------|-------------|
| `session_id` | string | Unique session identifier |
| `turn_number` | int | Which turn in the conversation (message_count / 2) |
| `message_count` | int | Total messages in conversation |
| `has_conversation_history` | bool | Whether agent has prior context (message_count > 2) |
| `files_in_context` | int | Number of files currently loaded in agent memory |
| `has_file_context` | bool | Whether agent has any files in memory |
| `tool_call_count` | int | Number of tools invoked during execution |
| `latency_seconds` | float | Total execution time |
| `success` | bool | Whether operation succeeded |
| `model` | string | LLM model used (e.g., gpt-4o-mini) |
| `temperature` | float | Model temperature setting |
| `input_length` | int | Character count of user input |
| `response_length` | int | Character count of response |
| `error_type` | string | Error class name (if failed) |

---

## 📝 Understanding Context Metrics

### `has_conversation_history` vs `has_file_context`

**`has_conversation_history: true`**
- Agent has prior messages in the conversation
- Can reference previous exchanges
- Useful for: Tracking multi-turn conversations
- Example: "Create a file" → "Now test it" (2nd message has history)

**`has_file_context: true`**
- Agent has file contents loaded in memory (via `read_file` tool)
- Can reference file contents without re-reading
- Useful for: Tracking when agent is working with specific files
- Example: After reading `config.py`, agent can reference its contents

**Current Implementation:**
- ✅ `has_conversation_history` - Tracks chat history (working)
- ⚠️ `has_file_context` - Tracks loaded files (not yet populated by tools)

**Note:** Currently `has_file_context` will always be `false` because tools don't populate the `current_files` state. This is a future enhancement for more advanced context tracking.

---

## 🔍 How to Use in LangSmith

### Filter by Tags

In LangSmith dashboard:

**Find all git operations:**
```
tag:git-operation
```

**Find slow queries:**
```
tag:slow
```

**Find errors:**
```
tag:error
```

**Combine filters:**
```
tag:git-operation AND tag:error
```

### Filter by Metadata

**Find sessions with high latency:**
```
metadata.latency_seconds > 5
```

**Find multi-turn conversations:**
```
metadata.turn_number > 3
```

**Find queries with many tool calls:**
```
metadata.tool_call_count > 2
```

**Find queries that used no tools:**
```
tag:no-tools OR metadata.tool_call_count = 0
```

**Find specific error types:**
```
metadata.error_type = "RuntimeError"
```

---

## 📊 Useful Queries

### Performance Analysis

**Average latency by task type:**
```
Group by: tag
Metric: avg(metadata.latency_seconds)
```

**Success rate by task type:**
```
Group by: tag
Metric: count(tag:success) / count(*)
```

### Error Analysis

**Most common errors:**
```
Filter: tag:error
Group by: metadata.error_type
```

**Error rate over time:**
```
Filter: tag:error
Chart: Time series
```

### Usage Patterns

**Most common task types:**
```
Group by: tag (file-creation, git-operation, etc.)
Metric: count(*)
```

**Average conversation length:**
```
Metric: avg(metadata.turn_number)
```

---

## 🎯 Example Use Cases

### 1. Find Slow Git Operations
```
tag:git-operation AND tag:slow
```
→ Identify which git commands are taking too long

### 2. Debug File Creation Errors
```
tag:file-creation AND tag:error
```
→ See what's failing when creating files

### 3. Analyze Multi-turn Performance
```
tag:multi-turn
Group by: metadata.turn_number
Metric: avg(metadata.latency_seconds)
```
→ Does performance degrade in long conversations?

### 4. Analyze Tool Usage Patterns
```
Group by: tag (no-tools, single-tool, multi-tool)
Metrics:
  - count(*)
  - avg(metadata.latency_seconds)
  - count(tag:success) / count(*)
```
→ Do more tool calls correlate with slower performance or lower success rate?

### 5. Find Complex Queries with Many Tools
```
tag:complex-query AND metadata.tool_call_count > 3
```
→ Identify the most demanding queries

### 6. Compare Model Performance
```
Group by: metadata.model
Metrics: 
  - avg(metadata.latency_seconds)
  - count(tag:success) / count(*)
```
→ Which model is faster/more reliable?

---

## 📈 Dashboards to Create

### 1. **Performance Dashboard**
- Average latency by task type
- P95 latency over time
- Slow query count (> 10s)

### 2. **Quality Dashboard**
- Success rate by task type
- Error rate over time
- Most common error types

### 3. **Usage Dashboard**
- Task type distribution
- Average conversation length
- Peak usage times

### 4. **Cost Dashboard**
- Token usage by task type
- Cost per session
- Most expensive queries

---

## 🚀 Next Steps

### Immediate
1. ✅ Tags and metadata now automatically added
2. ✅ Use filters in LangSmith to explore data
3. ✅ Create dashboards for key metrics

### Future Enhancements
- Add user feedback (thumbs up/down)
- Track tool call count per query
- Add cost per query
- Track code quality metrics
- Add A/B testing support

---

## 💡 Pro Tips

**1. Use tags for filtering, metadata for analysis**
- Tags: Categorical (git, file-creation, error)
- Metadata: Numerical (latency, turn_number, length)

**2. Combine filters for deep insights**
```
tag:git-operation AND tag:multi-turn AND metadata.latency_seconds > 5
```
→ Find slow git operations in long conversations

**3. Track trends over time**
- Group by date to see improvements
- Compare before/after code changes
- Identify regressions early

**4. Use metadata for alerts**
```
Alert: metadata.latency_seconds > 15
```
→ Get notified of performance issues

---

## 📚 Resources

- [LangSmith Filtering Docs](https://docs.smith.langchain.com/evaluation/filtering)
- [LangSmith Dashboards](https://docs.smith.langchain.com/observability/dashboards)
- [Custom Metadata Guide](https://docs.smith.langchain.com/tracing/metadata)

