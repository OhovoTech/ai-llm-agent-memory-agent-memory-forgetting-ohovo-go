"""Basic tests — pure local, instant."""

from agent_memory_forget import MemoryStore


def test_add_and_search():
    store = MemoryStore(":memory:")
    obs = store.add("hello world", importance=0.8, tags=["greeting"])
    assert obs.id
    hits = store.search("hello")
    assert len(hits) == 1
    assert hits[0].content == "hello world"
    store.close()


def test_forget():
    store = MemoryStore(":memory:")
    obs = store.add("to be forgotten")
    assert store.forget(obs.id) is True
    assert store.count() == 0
    store.close()


def test_prune():
    store = MemoryStore(":memory:", soft_limit=3)
    for i in range(5):
        store.add(f"item {i}", importance=i / 10)
    assert store.count() <= 3
    store.close()
