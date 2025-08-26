from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, UniqueConstraint
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class IssueActivity(Base):
    """Track issue activity for stale detection"""
    __tablename__ = "issue_activity"
    
    id = Column(Integer, primary_key=True)
    repo_name = Column(String(255), nullable=False)
    issue_number = Column(Integer, nullable=False)
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_stale = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (UniqueConstraint('repo_name', 'issue_number'),)

class RuleHistory(Base):
    """Track rule changes for audit purposes"""
    __tablename__ = "rule_history"
    
    id = Column(Integer, primary_key=True)
    rule_type = Column(String(50), nullable=False)  # 'label' or 'owner'
    action = Column(String(20), nullable=False)  # 'create', 'update', 'delete'
    rule_data = Column(Text, nullable=False)  # JSON string of the rule
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))