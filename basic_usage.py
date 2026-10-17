#!/usr/bin/env python3
"""Minimal example — runs instantly, no lag."""

from agent_memory_forget import MemoryStore

def main():
    store = MemoryStore(db_path=":memory:", soft_limit=20)

    # Add observations
    store.add("User prefers dark mode", importance=0.9, tags=["preference"])
    store.add("Tried approach A — failed with timeout", importance=0.7, tags=["failure"])
    store.add("Decision: use SQLite for local memory", importance=0.95, tags=["decision"])
    store.add("Temporary debug log line 1", importance=0.1, tags=["temp"])
    store.add("Temporary debug log line 2", importance=0.1, tags=["temp"])

    print(f"Total memories: {store.count()}")

    # Search
    hits = store.search("decision")
    print("Search 'decision':", [h.content for h in hits])

    # Intentional forget by tag
    deleted = store.forget_by_tag("temp")
    print(f"Forgot {deleted} temp items. Remaining: {store.count()}")

    # Time decay (simulate)
    store.apply_time_decay(half_life_hours=0.0001)  # aggressive for demo
    print("After decay, top memories:")
    for m in store.all(5):
        print(f"  [{m.importance:.2f}] {m.content}")

    store.close()
    print("Done — zero lag.")

if __name__ == "__main__":
    main()
