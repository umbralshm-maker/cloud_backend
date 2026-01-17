# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 23:47:02 2026

@author: ST
"""

# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .database import Base


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True)
    building_id = Column(String, unique=True, index=True, nullable=False)

    last_status = Column(String)
    last_lambda = Column(Float)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    event_id = Column(String, nullable=False)
    building_id = Column(String, ForeignKey("buildings.building_id"), nullable=False)

    status = Column(String, nullable=False)
    lambda_max = Column(Float)
    event_time = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("event_id", "building_id", name="uq_event_building"),
    )

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    building_id = Column(String, nullable=False, index=True)
    event_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    share_link = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "building_id", "event_id", "type",
            name="uq_report_event_type"
        ),
    )