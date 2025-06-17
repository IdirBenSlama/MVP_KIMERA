"""Neo4j session/driver factory.

This module centralises Neo4j connectivity so that **all** graph queries go
through the same connection pool.  Other packages should *only* import
`get_driver()` / `get_session()` rather than instantiating their own `neo4j.Driver`.

Environment variables
---------------------
NEO4J_URI   bolt URI (e.g. ``bolt://localhost:7687``)
NEO4J_USER  database username (defaults to ``neo4j``)
NEO4J_PASS  password
NEO4J_ENCRYPTED  "0" to disable encryption (default ``1``)

The driver is lazily initialised on first access to avoid slowing unit tests
when the graph is not required.
"""
from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from typing import Generator

from neo4j import GraphDatabase, Driver, Session

__all__ = ["get_driver", "get_session", "driver_liveness_check"]

# ---------------------------------------------------------------------------
# Internal state – lazily created singleton
# ---------------------------------------------------------------------------

_driver: Driver | None = None
_lock = threading.Lock()


def _create_driver() -> Driver:
    """Instantiate a Neo4j :class:`neo4j.Driver` from env vars."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASS", "neo4j")
    encrypted = os.getenv("NEO4J_ENCRYPTED", "1") != "0"

    return GraphDatabase.driver(
        uri,
        auth=(user, pwd),
        encrypted=encrypted,
        # tuned defaults – tweak as needed
        max_connection_lifetime=1800,  # seconds
        max_connection_pool_size=int(os.getenv("NEO4J_POOL_SIZE", "20")),
    )


def get_driver() -> Driver:
    """Return the lazily-initialised Neo4j driver (singleton)."""
    global _driver
    if _driver is None:
        with _lock:
            if _driver is None:  # double-checked locking
                _driver = _create_driver()
    return _driver


@contextmanager
def get_session(**kwargs) -> Generator[Session, None, None]:
    """Context manager yielding a Neo4j session.

    Example
    -------
    >>> from backend.graph.session import get_session
    >>> with get_session() as s:
    ...     s.run("RETURN 1").single()
    1
    """
    driver = get_driver()
    session: Session = driver.session(**kwargs)
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Health / readiness check helpers
# ---------------------------------------------------------------------------

def driver_liveness_check(timeout: float = 3.0) -> bool:
    """Quick *RETURN 1* to confirm the database is reachable."""
    try:
        with get_session() as s:
            record = s.run("RETURN 1 AS ok").single()
            return record["ok"] == 1
    except Exception:
        return False
