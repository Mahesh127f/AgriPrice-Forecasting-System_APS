from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aps.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(100))
    email        = Column(String(120), unique=True, index=True)
    password     = Column(String(200))
    state        = Column(String(80))
    district     = Column(String(80))
    role         = Column(String(20), default="farmer")
    created_at   = Column(DateTime, default=datetime.utcnow)
    alerts       = relationship("Alert", back_populates="user")
    saved_crops  = relationship("SavedCrop", back_populates="user")

class PriceRecord(Base):
    __tablename__ = "price_records"
    id           = Column(Integer, primary_key=True, index=True)
    crop         = Column(String(100), index=True)
    category     = Column(String(50))
    state        = Column(String(80))
    mandi        = Column(String(100))
    price        = Column(Float)
    arrivals     = Column(Float)
    date         = Column(DateTime, default=datetime.utcnow, index=True)

class Alert(Base):
    __tablename__ = "alerts"
    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    crop         = Column(String(100))
    alert_type   = Column(String(50))
    threshold    = Column(Float)
    is_active    = Column(Boolean, default=True)
    triggered    = Column(Boolean, default=False)
    created_at   = Column(DateTime, default=datetime.utcnow)
    user         = relationship("User", back_populates="alerts")

class SavedCrop(Base):
    __tablename__ = "saved_crops"
    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    crop         = Column(String(100))
    mandi        = Column(String(100))
    created_at   = Column(DateTime, default=datetime.utcnow)
    user         = relationship("User", back_populates="saved_crops")

class Report(Base):
    __tablename__ = "reports"
    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(200))
    crop         = Column(String(100))
    report_type  = Column(String(50))
    format       = Column(String(10))
    file_path    = Column(String(300))
    created_at   = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
