# create_db.py
from db.database import engine
import db.models

db.models.Base.metadata.create_all(bind=engine)
print("✅ Database tables created.")
