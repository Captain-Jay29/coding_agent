# Archived Files

## Old AgentExecutor Implementation

These files are from the previous LangChain AgentExecutor implementation.

**Archived on:** October 17, 2024

### Files:

- `agent.py` - Old CodingAgent class using AgentExecutor
- `memory.py` - Old SimpleMemoryManager with manual JSON serialization
- `state.py` - Old state management functions

### Why Archived?

Replaced by the new **LangGraph 2-Agent System** in `src/langgraph_agent/`

**New system benefits:**
- ✅ Proper 2-agent orchestration (Planning + Execution)
- ✅ Automatic memory via LangGraph checkpointing
- ✅ Better control flow with graph-based architecture
- ✅ Built-in state persistence
- ✅ Easier to extend and debug

### Migration

These files are kept for reference during the migration period.
Once the LangGraph system is fully integrated with CLI/Web UI, these can be removed.

