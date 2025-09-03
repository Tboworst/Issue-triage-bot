from app import db
from sqlalchemy import UniqueConstraint
from datetime import datetime, timezone


class IssueActivity(db.Model):
    """Track issue activity for stale detection"""

    __tablename__ = "issue_activity"

    id = db.Column(db.Integer, primary_key=True)
    repo_full_name = db.Column(db.String(255), nullable=False)
    issue_number = db.Column(db.Integer, nullable=False)
    last_activity = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_stale = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("repo_full_name", "issue_number"),)


class RuleHistory(db.Model):
    """Track rule changes for audit purposes"""

    __tablename__ = "rule_history"

    id = db.Column(db.Integer, primary_key=True)
    #take from labels and owners 
    rule_type = db.Column(db.String(50), nullable=False) 
    action = db.Column(db.String(20), nullable=False) 
    rule_data = db.Column(db.Text, nullable=False)  
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
