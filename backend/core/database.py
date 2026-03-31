from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Simulation(Base):
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    target = Column(String, nullable=False)
    scenario = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    config = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)


class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, nullable=False)
    agent_type = Column(String, nullable=False)
    persona = Column(String, nullable=True)
    status = Column(String, default="idle")
    created_at = Column(DateTime, default=datetime.utcnow)
    memory = Column(JSON, nullable=True)
    actions = Column(JSON, nullable=True)


class Action(Base):
    __tablename__ = "actions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, nullable=False)
    simulation_id = Column(Integer, nullable=False)
    action_type = Column(String, nullable=False)
    mitre_tactic = Column(String, nullable=True)
    mitre_technique = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    result = Column(JSON, nullable=True)
    success = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class GodModeInjection(Base):
    __tablename__ = "god_mode_injections"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, nullable=False)
    injection_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    config = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
