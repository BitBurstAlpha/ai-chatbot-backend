from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db 


class Chatbot(db.Model):
    __tablename__ = 'chatbot'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False, index=True)
    user_id = db.Column(db.String(50), nullable=False, index=True)
  
    
    def __init__(self, user_id, title):
        self.user_id = user_id
        self.title = title
        self.created_at = datetime.now(timezone.utc)


class ChatbotKnowledge(db.Model):
    __tablename__ = 'chatbot_knowledge'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    chatbot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chatbot.id'), nullable=False)
    knowledge_id = db.Column(db.String(50), nullable=False, index=True)
    
    def __init__(self, chatbot_id, knowledge_id):
        self.chatbot_id = chatbot_id
        self.knowledge_id = knowledge_id
        self.created_at = datetime.now(timezone.utc)
        