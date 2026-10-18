# LLM Agent Memory - Agent Memory Forgetting Ohovo Memoo Go

**Simple AI Agent Memory Tool with Automatic Forgetting**

This tool gives AI agents a real memory.
It helps AI agents remember important things and forget old things so they stay fast and smart.

It solves the problem of AI agents becoming slow or forgetting important information.

## What is this tool?

This is a free Python tool that stores memories on your computer.
It works with Claude, ChatGPT, Grok, Gemini, Cursor, and any tool that can run Python.

## Who can use it?

Anyone who uses AI agents and wants better memory.

## Compatible with

- Claude
- ChatGPT
- Grok
- Gemini
- Cursor
- Google Colab
- Any tool that can run Python code

---

## How to use this tool (Very Easy Steps)

You do **not** need to create any file.
Just copy and paste the code directly into the chat.

---

### Step 1: Install the tool

**What this does?**
This installs the memory tool.

**Where to paste?**
Copy the code below and paste it into your AI chat (Claude, ChatGPT, Cursor, etc.), then press Enter.

```bash
pip install -e .

What you will see?

The tool will start installing. Wait until it finishes.

Step 2: Load the memory tool

What this does?

This loads the memory tool so you can use it.

Where to paste?

Copy code below & paste it into the same chat. The code that says: from agent_memory_forget import MemoryStore

from agent_memory_forget import MemoryStore
```

**What you will see?**

Nothing special. It just loads the tool silently.

---

### Step 3: Create a memory store

**What this does?**

This creates a place to save memories on your computer.

**Where to paste?**

Copy the code below and paste it into the same chat.

```python
store = MemoryStore("my_memory.db")
```

**What you will see?**

Nothing appears. It only creates the memory place.

---

### Step 4: Add a memory

**What this does?**

This saves a new memory.

**Where to paste?**

Copy the code below and paste it into the same chat.

```python
store.add("User likes dark mode and short answers", importance=0.9)
```

**What you will see?**

The memory is saved silently. No message will show.

---

### Step 5: Search for a memory

**What this does?**

This finds memories that match your words.

**Where to paste?**

Copy the code below and paste it into the same chat.

```python
results = store.search("dark mode", limit=5)
print(results)
```

**What you will see?**

You will see the memories that match “dark mode”.

---

### Step 6: Forget old memories

**What this does?**

This removes old or less important memories.

**Where to paste?**

Copy the code below and paste it into the same chat.

```python
store.forget(older_than_days=30, min_importance=0.3)
print("Remaining memories:", store.count())
```

**What you will see?**

You will see how many memories are left.

---

## Full Example (Copy everything together)

You can also copy and paste all the code below at once in the chat:

```python
from agent_memory_forget import MemoryStore

store = MemoryStore("my_memory.db")

store.add("User likes dark mode and short answers", importance=0.9)

results = store.search("dark mode", limit=5)
print(results)

store.forget(older_than_days=30, min_importance=0.3)
print("Remaining memories:", store.count())
```

---

## License

Apache-2.0

Free for personal and commercial use.
