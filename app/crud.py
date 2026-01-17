# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 23:47:51 2026

@author: ST
"""

# app/crud.py
from sqlalchemy.orm import Session
from . import models


def upsert_building(db: Session, building_id: str, status: str, lambda_max):
    b = db.query(models.Building).filter_by(building_id=building_id).first()
    if not b:
        b = models.Building(
            building_id=building_id,
            last_status=status,
            last_lambda=lambda_max
        )
        db.add(b)
    else:
        b.last_status = status
        b.last_lambda = lambda_max
    db.commit()


def upsert_event(
    db: Session,
    building_id: str,
    event_id: str,
    status: str,
    lambda_max,
    event_time
):
    ev = (
        db.query(models.Event)
        .filter_by(event_id=event_id, building_id=building_id)
        .first()
    )

    if ev:
        # Evento ya existe → actualiza solo lo permitido
        ev.status = status
        ev.lambda_max = lambda_max
        ev.event_time = event_time
    else:
        ev = models.Event(
            building_id=building_id,
            event_id=event_id,
            status=status,
            lambda_max=lambda_max,
            event_time=event_time
        )
        db.add(ev)

    db.commit()


def upsert_report(db: Session, event_id: str, rtype: str, link: str):
    r = (
        db.query(models.Report)
        .filter_by(event_id=event_id, type=rtype)
        .first()
    )
    if not r:
        r = models.Report(event_id=event_id, type=rtype, share_link=link)
        db.add(r)
    else:
        r.share_link = link
    db.commit()

def get_all_buildings(db: Session):
    return db.query(models.Building).all()


def get_building(db: Session, building_id: str):
    return (
        db.query(models.Building)
        .filter_by(building_id=building_id)
        .first()
    )


def get_event(db: Session, event_id: str):
    return (
        db.query(models.Event)
        .filter_by(event_id=event_id)
        .order_by(models.Event.created_at.desc())
        .first()
    )


def get_reports_for_event(db: Session, event_id: str):
    return (
        db.query(models.Report)
        .filter_by(event_id=event_id)
        .all()
    )