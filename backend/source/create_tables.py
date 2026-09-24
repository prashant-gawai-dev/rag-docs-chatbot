from database import Base, engine
from model import DocumentChunk ,DocumentChunkV2

if engine is not None:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")
else:
    print("No DATABASE_URL found - check .env file")
