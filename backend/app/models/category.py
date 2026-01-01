from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # e.g., "Music", "Fashion", "Slang"
    description = Column(String, nullable=True)  # Brief description of the category
    
    def __repr__(self):
        return f"<Category {self.name}>"