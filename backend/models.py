from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    profile_data = Column(JSON) # Skills, projects, experience
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job_leads = relationship("JobLead", back_populates="user")
    interviews = relationship("InterviewSession", back_populates="user")

class JobLead(Base):
    __tablename__ = "job_leads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    company = Column(String)
    url = Column(String, unique=True)
    status = Column(String, default="discovered") # discovered, applied, interviewed, offered, rejected
    metadata_info = Column(JSON) # Hiring manager, skills, salary est, etc.
    battle_card = Column(JSON, nullable=True) # Full War Room result
    is_elite = Column(Boolean, default=False) # Flag for >90% matches
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="job_leads")
    interviews = relationship("InterviewSession", back_populates="job")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("job_leads.id"))
    question = Column(Text)
    answer = Column(Text)
    evaluation = Column(JSON)
    audio_path = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="interviews")
    job = relationship("JobLead", back_populates="interviews")
