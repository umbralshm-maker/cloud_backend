# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 23:47:28 2026

@author: ST
"""

# app/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict
from typing import List

class AlertIn(BaseModel):
    building_id: str
    event_id: str
    lambda_max: Optional[float] = None
    status: Optional[str] = None
    event_time: Optional[str] = None


class ReportLink(BaseModel):
    share_link: str


class ReportLinks(BaseModel):
    alerta: Optional[ReportLink] = None
    evento: Optional[ReportLink] = None
    mensual: Optional[ReportLink] = None


class ReportLinksIn(BaseModel):
    building_id: str
    event_id: str
    reports: ReportLinks

class BuildingOut(BaseModel):
    building_id: str
    last_status: Optional[str]
    last_lambda: Optional[float]

    class Config:
        orm_mode = True


class EventOut(BaseModel):
    event_id: str
    building_id: str
    status: str
    lambda_max: Optional[float]
    event_time: Optional[str]

    class Config:
        orm_mode = True


class ReportOut(BaseModel):
    type: str
    share_link: str

    class Config:
        orm_mode = True
