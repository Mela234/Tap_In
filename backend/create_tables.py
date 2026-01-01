from app.core.database import engine, Base
from app.models import Category, RawData, Trend, User

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")