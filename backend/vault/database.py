from sqlalchemy import create_engine, Column, String, Float, JSON, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
 mm4812-codex/implement-vector-search-for-geoids
from typing import Any

=======
 main
try:
    from pgvector.sqlalchemy import Vector
except Exception:  # pragma: no cover - allows sqlite tests without pgvector
    Vector = None  # type: ignore
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kimera_swm.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
if DATABASE_URL.startswith("postgresql"):
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ScarDB(Base):
    __tablename__ = "scars"

    scar_id = Column(String, primary_key=True, index=True)
    geoids = Column(JSON)
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved_by = Column(String)
    pre_entropy = Column(Float)
    post_entropy = Column(Float)
    delta_entropy = Column(Float)
    cls_angle = Column(Float)
    semantic_polarity = Column(Float)
    mutation_frequency = Column(Float)
    vault_id = Column(String, index=True)


class GeoidDB(Base):
    __tablename__ = "geoids"

    geoid_id = Column(String, primary_key=True, index=True)
    symbolic_state = Column(JSON)
    metadata_json = Column(JSON)
 mm4812-codex/implement-vector-search-for-geoids
=======
    semantic_state_json = Column(JSON)
 main
    if DATABASE_URL.startswith("postgresql") and Vector is not None:
        semantic_vector = Column(Vector(384))  # type: ignore
    else:
        # Fallback for sqlite - store vector as JSON list
        semantic_vector = Column(JSON)

 mm4812-codex/implement-vector-search-for-geoids
=======

 main
# Create tables if they don't exist
Base.metadata.create_all(bind=engine)
