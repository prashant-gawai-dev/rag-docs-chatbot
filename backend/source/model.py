from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from database import Base
import logging

logger = logging.getLogger(__name__)
logger.info("Model/ Entered in model")

class DocumentChunk(Base):
   __tablename__ = "document_chunks"
   id = Column(Integer, primary_key=True, index=True)
   source_file = Column(String)
   content = Column(Text)
   embedding = Column(Vector(384))
logger.info("Model/ Model execution completed")

class DocumentChunkV2(Base):
   __tablename__ = "Gpi_document_chunks"
   id = Column(Integer, primary_key=True, index=True)
   source_file = Column(String)
   content = Column(Text)
   embedding = Column(Vector(384))
logger.info("Model/ Model execution completed")