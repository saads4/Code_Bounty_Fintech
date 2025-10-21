from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.db import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    category = Column(String, index=True)
    description = Column(String, default="")
    amount = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
