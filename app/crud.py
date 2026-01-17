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


def create_placeholder_event(db: Session, building_id: str, event_id: str):
    ev = models.Event(
        building_id=building_id,
        event_id=event_id,
        status="SIN_DATOS",
        lambda_max=None,
        event_time=None
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


def upsert_report(
    db: Session,
    building_id: str,
    event_id: str,
    rtype: str,
    link: str
):
    r = (
        db.query(models.Report)
        .filter_by(
            building_id=building_id,
            event_id=event_id,
            type=rtype
        )
        .first()
    )

    if not r:
        r = models.Report(
            building_id=building_id,
            event_id=event_id,
            type=rtype,
            share_link=link
        )
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


def get_event(db: Session, building_id: str, event_id: str):
    return (
        db.query(models.Event)
        .filter_by(building_id=building_id, event_id=event_id)
        .first()
    )


def get_reports_for_event(db: Session, building_id: str, event_id: str):
    return (
        db.query(models.Report)
        .filter_by(building_id=building_id, event_id=event_id)
        .all()
    )
