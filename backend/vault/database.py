from sqlalchemy import create_engine, Column, String, Float, Integer, JSON, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kimera_swm.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
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

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)
