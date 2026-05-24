import os
import math
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///D:/DocuStreamAI/docustream.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LogRecord(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String(50), default=datetime.utcnow().isoformat)
    raw_log = Column(Text, nullable=False)
    severity_level = Column(String(20), nullable=False)
    service_name = Column(String(50), nullable=False)
    root_cause = Column(Text, nullable=False)
    severity_score = Column(Float, nullable=False)
    alert_triggered = Column(Boolean, default=False)
    data_type = Column(String(20), default="OTHER")
    vector_x = Column(Float, default=50.0)
    vector_y = Column(Float, default=50.0)

# Create tables
Base.metadata.create_all(bind=engine)

# Auto-migrate: ensure data_type column exists in existing database
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE logs ADD COLUMN data_type VARCHAR(20) DEFAULT 'OTHER'"))
        conn.commit()
except Exception:
    # If the column already exists or text import fails, skip silently
    pass

def get_db():
    db = SessionLocal()
    try:
      yield db
    finally:
      db.close()

# Ingest and assign coordinates
def add_log_entry(db_session, log_text: str, structured_data) -> LogRecord:
    service = structured_data.service_name.lower()
    
    centers = {
        "neural-link": (25, 70),
        "auth-service": (75, 75),
        "replicator-control": (50, 40),
        "propulsion-engine": (40, 20),
        "db-pool": (20, 30)
    }
    
    base_x, base_y = centers.get(service, (50, 50))
    dispersion = (10 - structured_data.severity_score) * 1.5 + 2.0
    random_angle = np.random.rand() * 2 * math.pi
    random_dist = np.random.rand() * dispersion
    
    x = float(np.clip(base_x + math.cos(random_angle) * random_dist, 5.0, 95.0))
    y = float(np.clip(base_y + math.sin(random_angle) * random_dist, 5.0, 95.0))

    db_entry = LogRecord(
        raw_log=log_text,
        timestamp=structured_data.timestamp,
        severity_level=structured_data.severity_level,
        service_name=structured_data.service_name,
        root_cause=structured_data.root_cause,
        severity_score=structured_data.severity_score,
        alert_triggered=structured_data.alert_triggered,
        data_type=getattr(structured_data, 'data_type', 'OTHER'),
        vector_x=x,
        vector_y=y
    )
    
    db_session.add(db_entry)
    db_session.commit()
    db_session.refresh(db_entry)
    return db_entry

# Jaccard Search
def get_words(text: str) -> set:
    return set(text.lower().replace(",", " ").replace(".", " ").replace(":", " ").split())

def compute_jaccard_similarity(text1: str, text2: str) -> float:
    words1 = get_words(text1)
    words2 = get_words(text2)
    if not words1 or not words2:
      return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return float(len(intersection)) / len(union)

def search_semantic_logs(db_session, query: str, limit: int = 8):
    all_logs = db_session.query(LogRecord).all()
    if not all_logs:
        return []
        
    results = []
    for log in all_logs:
        similarity_text = f"{log.raw_log} {log.root_cause} {log.service_name} {log.severity_level}"
        sim = compute_jaccard_similarity(query, similarity_text)
        
        query_words = get_words(query)
        match_count = sum(1 for qw in query_words if qw in similarity_text.lower())
        if len(query_words) > 0:
            sim += (match_count / len(query_words)) * 0.4
            
        sim = min(1.0, sim)
        results.append((log, sim))
        
    results.sort(key=lambda item: item[1], reverse=True)
    return results[:limit]
