from sqlalchemy import Column, Integer, String, Text, ForeignKey
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True) # FIXED: removed the 'v'
    password = Column(String(100))

class Report(Base): # FIXED: Changed to singular Report to match app.py
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resume_text = Column(Text)
    results = Column(Text) # FIXED: Changed to results to match app.py