from sqlalchemy import Column, Integer, String
from app.core.db.base import Base

class User(Base):
    __tablename__ = "users"
    description = Column(String, nullable=True)
    name = Column(String, nullable=False)
