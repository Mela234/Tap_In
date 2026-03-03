from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_subscribed = Column(Boolean, default=False)
    is_email_subscriber = Column(Boolean, default=False)  # For bi-weekly email digest
    last_email_sent = Column(DateTime, nullable=True)  # Track when last email was sent
    created_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User {self.email}>"