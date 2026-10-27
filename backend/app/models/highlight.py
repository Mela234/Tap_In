from sqlalchemy import Column, Integer, String, Text, Date, DateTime, JSON
from datetime import datetime
from app.core.database import Base


class Highlight(Base):
    """One summarized story in a daily edition, shown on a side of the hexagon."""

    __tablename__ = "highlights"

    id = Column(Integer, primary_key=True, index=True)
    edition = Column(Date, nullable=False, index=True)  # the day this highlight was published
    topic = Column(String, nullable=False, index=True)  # "tech", "entertainment", "culture", ...
    rank = Column(Integer, nullable=False)  # 1 = biggest story on that side

    title = Column(String, nullable=False)
    gist = Column(Text, nullable=False)
    why_it_matters = Column(Text, nullable=True)

    sources = Column(JSON, nullable=False, default=list)  # [{"name": "BBC", "url": "..."}]
    coverage = Column(Integer, default=1)  # how many outlets covered the story

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Highlight {self.topic}: {self.title}>"
