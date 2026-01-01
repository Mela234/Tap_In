from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from app.core.database import Base


class RawData(Base):
    __tablename__ = "raw_data"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)  # "reddit", "youtube", "google_trends"
    data_type = Column(String, nullable=False)  # "post", "video", "search_query"
    content = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)
    url = Column(String, nullable=True) 
    collected_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<RawData from {self.source}>"