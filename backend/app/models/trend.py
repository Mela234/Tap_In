from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Trend(Base):
    __tablename__ = "trends"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  
    description = Column(Text, nullable=False) 
    why_it_matters = Column(Text, nullable=True)  
    how_to_talk_about_it = Column(Text, nullable=True) 
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category")
    
    relevance_score = Column(Float, default=0.0) 
    sources = Column(String, nullable=True)  
    
    week_start = Column(DateTime, nullable=False)  
    week_end = Column(DateTime, nullable=False)  
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Trend {self.title}>"