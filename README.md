# Ohovo Memoo – AI Agent Memory with Intentional Forgetting

**Local-first persistent memory for AI agents with built-in intentional forgetting.**  
Solves context rot, unbounded memory growth, and context inertia.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Local-first](https://img.shields.io/badge/local--first-yes-brightgreen.svg)](#)

## What is Ohovo Memoo?

Ohovo Memoo (package name: `agent-memory-forget`) is a lightweight Python library that gives AI agents long-term memory while automatically pruning old or low-value information. It runs completely locally using SQLite, has almost zero dependencies, and is designed for real-time use with no lag on the hot path.

It is ideal for developers building autonomous agents, coding assistants, or multi-session AI systems who need memory that does not grow forever.

## Compatible AI Models & Frameworks

Works with **any** LLM or agent framework that can call Python functions or read/write local files:

- Claude (Anthropic) / Claude Code
- GPT-4o, o1, o3 (OpenAI) / Codex
- Grok (xAI)
- Gemini (Google)
- Local models via Ollama, llama.cpp, vLLM, LM Studio
- Agent frameworks: LangGraph, CrewAI, AutoGen, OpenHands, Cursor, Continue, Aider, custom agents

No model-specific API is required for the core memory features.

## Installation

```bash
# From the package folder
pip install -e .

# Or later when published
# pip install ohovo-memoo
```

## Quick Start (30 seconds)

```python
from agent_memory_forget import MemoryStore

# Create a local memory store (SQLite file)
store = MemoryStore("my_agent_memory.db")

# Add memories with optional importance score (0.0 – 1.0)
store.add("User prefers dark mode and concise answers", importance=0.9)
store.add("Decision: use SQLite for local memory", importance=0.95)
store.add("Temporary note about current session", importance=0.2)

# Search for relevant memories
results = store.search("user interface preferences", limit=5)
for r in results:
    print(r)

# Intentionally forget old or low-value memories
store.forget(older_than_days=30, min_importance=0.3)

print("Remaining memories:", store.count())
```

## How to Use – Full User Guide

### 1. Creating a Memory Store
```python
store = MemoryStore("path/to/memory.db")  # creates the file if it does not exist
```

### 2. Adding Memories
```python
store.add(text: str, importance: float = 0.5, metadata: dict = None)
```
- `importance` helps the forgetting engine decide what to keep.
- You can attach optional metadata (source, timestamp, tags, etc.).

### 3. Searching Memories
```python
results = store.search(query: str, limit: int = 5)
```
Returns the most relevant memories (keyword-based by default, fast and local).

### 4. Intentional Forgetting
```python
store.forget(
    older_than_days: int = None,
    min_importance: float = None,
    max_count: int = None
)
```
Three complementary strategies:
- Time-based decay
- Importance threshold
- Hard limit on total memories

This directly addresses the “context rot” and “unbounded growth” problems still open in many agent memory GitHub issues.

### 5. Integration Pattern with Agents
Most agents can call tools. Expose these simple functions as tools:

- `add_memory(text, importance)`
- `search_memory(query)`
- `forget_old_memories(...)`

The agent decides when to store or retrieve information. Because everything is local and fast, there is no noticeable latency.

## Why Ohovo Memoo?

- Completely local – no API keys required for core features
- Extremely fast (Python stdlib + SQLite)
- Solves real pain points still visible in open GitHub issues in 2026
- Designed so you can later add paid hosted consolidation, memory packs, or private storage tiers

## Example Output

```
Total memories: 5
Search 'decision': ['Decision: use SQLite for local memory']
Forgot 2 temp items. Remaining: 3
After decay, top memories:
  [0.95] Decision: use SQLite for local memory
  [0.90] User prefers dark mode
  [0.70] Tried approach A — failed with timeout
Done — zero lag.
```

## License

Apache-2.0 – free for commercial use.

## Contributing

Issues and pull requests are welcome. Focus on real-time performance and minimal dependencies.
