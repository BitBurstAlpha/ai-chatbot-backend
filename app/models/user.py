from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db 
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")  # User or Admin
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __init__(self, email, password, role="user"):
        self.email = email
        self.set_password(password)  # This hashes the password when the user is created
        self.role = role
        self.created_at = datetime.now(timezone.utc)

    def set_password(self, password):
        """Hashes and sets the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks the password hash."""
        return check_password_hash(self.password_hash, password)  # No re-hashing needed