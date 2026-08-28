import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Table
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.utils.enums import VideoStatus, CustomerStatus, BasketStatus, AlertSeverity, AlertStatus, IncidentStatus

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    processed_video_path = Column(String(512), nullable=True)
    duration_seconds = Column(Float, default=0.0)
    total_frames = Column(Integer, default=0)
    current_frame = Column(Integer, default=0)
    progress_percent = Column(Float, default=0.0)
    processing_status = Column(String(50), default=VideoStatus.UPLOADED.value)
    status_message = Column(String(255), default="Uploaded & Ready for Processing")
    upload_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customers = relationship("Customer", back_populates="video", cascade="all, delete-orphan")
    baskets = relationship("Basket", back_populates="video", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="video", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="video", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="video", cascade="all, delete-orphan")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(String(100), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    status = Column(String(50), default=CustomerStatus.ACTIVE.value)
    entry_time = Column(DateTime, default=datetime.utcnow)
    last_seen_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    total_stay_seconds = Column(Float, default=0.0)
    current_zone = Column(String(100), default="entrance")
    current_risk_score = Column(Float, default=0.0)
    risk_level = Column(String(50), default="LOW")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="customers")
    baskets = relationship("Basket", back_populates="associated_customer")
    events = relationship("Event", back_populates="customer")
    alerts = relationship("Alert", back_populates="customer")
    incidents = relationship("Incident", back_populates="customer")

class Basket(Base):
    __tablename__ = "baskets"

    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(String(100), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    status = Column(String(50), default=BasketStatus.ACTIVE.value)
    associated_customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    first_seen_time = Column(DateTime, default=datetime.utcnow)
    last_seen_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="baskets")
    associated_customer = relationship("Customer", back_populates="baskets")
    events = relationship("Event", back_populates="basket")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    basket_id = Column(Integer, ForeignKey("baskets.id"), nullable=True)
    event_type = Column(String(100), nullable=False, index=True)
    timestamp_seconds = Column(Float, nullable=False, default=0.0)
    event_time = Column(DateTime, default=datetime.utcnow)
    zone = Column(String(100), nullable=True)
    confidence = Column(Float, default=1.0)
    metadata_json = Column(Text, nullable=True, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="events")
    customer = relationship("Customer", back_populates="events")
    basket = relationship("Basket", back_populates="events")
    alerts = relationship("Alert", back_populates="event")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    severity = Column(String(50), default=AlertSeverity.LOW.value)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    risk_score = Column(Float, default=0.0)
    status = Column(String(50), default=AlertStatus.ACTIVE.value)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="alerts")
    customer = relationship("Customer", back_populates="alerts")
    event = relationship("Event", back_populates="alerts")
    incidents = relationship("Incident", back_populates="alert")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    incident_type = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    risk_score = Column(Float, default=0.0)
    incident_status = Column(String(50), default=IncidentStatus.OPEN.value)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="incidents")
    customer = relationship("Customer", back_populates="incidents")
    alert = relationship("Alert", back_populates="incidents")

class RiskSettings(Base):
    __tablename__ = "risk_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
