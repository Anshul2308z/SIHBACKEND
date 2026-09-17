from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sihbackend.db.database import Base

# 1. History (Persistence for user sessions/reports)
class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True) # E.g., device ID or user ID
    query = Column(String, nullable=False)
    jurisdiction = Column(String, default="India")
    report_data = Column(JSON, nullable=True) # Full structured RAG analysis
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 2. ReferenceData: Plant/Botanical records
class Plant(Base):
    __tablename__ = "reference_plants"
    
    id = Column(String, primary_key=True, index=True) # e.g. "P001"
    name = Column(String, index=True, nullable=False)
    botanical_name = Column(String, nullable=False)
    family = Column(String)
    tkdl_status = Column(Boolean, default=False)
    abs_risk = Column(String) # e.g. "Review required"

# 3. ReferenceData: Sources Registry
class Source(Base):
    __tablename__ = "reference_sources"
    
    id = Column(String, primary_key=True, index=True) # e.g. "tkdl", "uspto"
    name = Column(String, nullable=False)
    authority = Column(String)
    jurisdiction = Column(String)
    url = Column(String)
    last_verified = Column(String)

# 4. ReferenceData: Jurisdictions
class Jurisdiction(Base):
    __tablename__ = "reference_jurisdictions"
    
    id = Column(String, primary_key=True, index=True) # e.g. "IN", "WO"
    name = Column(String, nullable=False) # e.g. "India", "International"
    regulator = Column(String)
    patent_duration_years = Column(Integer, default=20)
