from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db 


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.String(50), nullable=False, index=True)
    query = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='open', index=True)
    agent_id = db.Column(db.String(50), nullable=True, index=True)

    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    last_user_reply_at = db.Column(db.DateTime, nullable=True)
    last_agent_reply_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship with replies
    replies = db.relationship('TicketReply', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id, query, agent_id=None, status='open'):
        self.user_id = user_id
        self.query = query
        self.agent_id = agent_id
        self.status = status
        self.created_at = datetime.now(timezone.utc)

    def __repr__(self):
        return f"<Ticket id={self.id} status={self.status}>"

class TicketReply(db.Model):
    __tablename__ = 'ticket_replies'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.String(36), nullable=True)  # If reply is from the user
    agent_id = db.Column(db.String(36), nullable=True)  # If reply is from an agent
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __init__(self, ticket_id, message, user_id=None, agent_id=None):
        self.ticket_id = ticket_id
        self.message = message
        self.user_id = user_id
        self.agent_id = agent_id
        self.created_at = datetime.now(timezone.utc)