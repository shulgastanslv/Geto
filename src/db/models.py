from sqlalchemy import Column, DateTime, String,Integer, TEXT
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

class Base(AsyncAttrs,DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=200), index=True)

class ScheduledMessage(Base):
    __tablename__ = 'scheduled_messages'
    
    id = Column(Integer, primary_key=True, index=True)
    scheduler_id = Column(Integer, index=True)
    recipient_id = Column(Integer, index=True)
    message = Column(TEXT)
    scheduled_time = Column(DateTime, index=True)