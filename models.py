from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Double, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class File(Base):
    __tablename__ = 'files'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    size = Column(Double, nullable=False, default=0)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

class FileCreate(BaseModel):
    name: str
    size: float
    content_type: str