"""
Core memory store with intentional forgetting.

Design goals:
- Local, zero external deps for core path (uses stdlib sqlite3)
- Fast add / search / forget
- Explicit decay and pressure-based pruning to fight context inertia
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, List, Optional


@dataclass
class Observation:
    id: str
    content: str
    importance: float = 0.5          # 0.0 – 1.0
    created_at: float = 0.0
    last_accessed: float = 0.0
    tags: List[str] | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
        if self.last_accessed == 0.0:
            self.last_accessed = self.created_at
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class MemoryStore:
    """
    Simple SQLite-backed memory with intentional forgetting.

    Forgetting strategies:
    - time_decay: older memories lose importance
    - access_decay: rarely accessed lose importance
    - pressure: when count exceeds soft limit, prune lowest importance
    - explicit forget(id) or forget_by_tag()
    """

    def __init__(self, db_path: str | Path = ":memory:", soft_limit: int = 500):
        self.db_path = str(db_path)
        self.soft_limit = soft_limit
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                importance REAL NOT NULL DEFAULT 0.5,
                created_at REAL NOT NULL,
                last_accessed REAL NOT NULL,
                tags TEXT NOT NULL DEFAULT '[]',
                metadata TEXT NOT NULL DEFAULT '{}'
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_importance ON observations(importance DESC)"
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_created ON observations(created_at)"
        )
        self._conn.commit()

    def add(
        self,
        content: str,
        importance: float = 0.5,
        tags: List[str] | None = None,
        metadata: dict | None = None,
    ) -> Observation:
        obs = Observation(
            id=str(uuid.uuid4()),
            content=content,
            importance=max(0.0, min(1.0, importance)),
            tags=tags or [],
            metadata=metadata or {},
        )
        self._conn.execute(
            """
            INSERT INTO observations (id, content, importance, created_at, last_accessed, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                obs.id,
                obs.content,
                obs.importance,
                obs.created_at,
                obs.last_accessed,
                json.dumps(obs.tags),
                json.dumps(obs.metadata),
            ),
        )
        self._conn.commit()
        self._maybe_prune()
        return obs

    def get(self, obs_id: str) -> Optional[Observation]:
        row = self._conn.execute(
            "SELECT * FROM observations WHERE id = ?", (obs_id,)
        ).fetchone()
        if not row:
            return None
        return self._row_to_obs(row)

    def search(
        self,
        query: str,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> List[Observation]:
        """Simple keyword search (case-insensitive). Fast and lag-free."""
        q = f"%{query.lower()}%"
        rows = self._conn.execute(
            """
            SELECT * FROM observations
            WHERE lower(content) LIKE ? AND importance >= ?
            ORDER BY importance DESC, last_accessed DESC
            LIMIT ?
            """,
            (q, min_importance, limit),
        ).fetchall()
        results = []
        for row in rows:
            obs = self._row_to_obs(row)
            # touch last_accessed
            self._conn.execute(
                "UPDATE observations SET last_accessed = ? WHERE id = ?",
                (time.time(), obs.id),
            )
            results.append(obs)
        self._conn.commit()
        return results

    def forget(self, obs_id: str) -> bool:
        cur = self._conn.execute("DELETE FROM observations WHERE id = ?", (obs_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def forget_by_tag(self, tag: str) -> int:
        rows = self._conn.execute("SELECT id, tags FROM observations").fetchall()
        deleted = 0
        for row in rows:
            tags = json.loads(row["tags"])
            if tag in tags:
                self._conn.execute("DELETE FROM observations WHERE id = ?", (row["id"],))
                deleted += 1
        self._conn.commit()
        return deleted

    def apply_time_decay(self, half_life_hours: float = 24.0) -> int:
        """Reduce importance of old memories. Returns number of updated rows."""
        now = time.time()
        half_life_sec = half_life_hours * 3600
        rows = self._conn.execute("SELECT id, importance, created_at FROM observations").fetchall()
        updated = 0
        for row in rows:
            age = now - row["created_at"]
            # exponential decay
            factor = 0.5 ** (age / half_life_sec)
            new_imp = max(0.01, row["importance"] * factor)
            if abs(new_imp - row["importance"]) > 0.001:
                self._conn.execute(
                    "UPDATE observations SET importance = ? WHERE id = ?",
                    (new_imp, row["id"]),
                )
                updated += 1
        self._conn.commit()
        return updated

    def prune_to_limit(self, hard_limit: int | None = None) -> int:
        """Remove lowest-importance memories until under limit."""
        limit = hard_limit or self.soft_limit
        count = self._conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        if count <= limit:
            return 0
        to_remove = count - limit
        rows = self._conn.execute(
            "SELECT id FROM observations ORDER BY importance ASC, last_accessed ASC LIMIT ?",
            (to_remove,),
        ).fetchall()
        for row in rows:
            self._conn.execute("DELETE FROM observations WHERE id = ?", (row["id"],))
        self._conn.commit()
        return len(rows)

    def _maybe_prune(self) -> None:
        count = self._conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        if count > self.soft_limit:
            self.prune_to_limit(self.soft_limit)

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]

    def all(self, limit: int = 100) -> List[Observation]:
        rows = self._conn.execute(
            "SELECT * FROM observations ORDER BY importance DESC LIMIT ?", (limit,)
        ).fetchall()
        return [self._row_to_obs(r) for r in rows]

    def _row_to_obs(self, row: sqlite3.Row) -> Observation:
        return Observation(
            id=row["id"],
            content=row["content"],
            importance=row["importance"],
            created_at=row["created_at"],
            last_accessed=row["last_accessed"],
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
        )

    def close(self) -> None:
        self._conn.close()
