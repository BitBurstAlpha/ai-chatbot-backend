from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db 


class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    s3_key = db.Column(db.String, nullable=False)
    original_filename = db.Column(db.String, nullable=False)
    file_type = db.Column(db.String(10))
    file_size = db.Column(db.Integer) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self, user_id , title, description,s3_key,original_filename, file_type, file_size):
            self.title = title,
            self.user_id = user_id,
            self.description = description,
            self.s3_key = s3_key,
            self.original_filename = original_filename,
            self.file_type = file_type,
            self.file_size = file_size,
            self.created_at = datetime.now(timezone.utc)
