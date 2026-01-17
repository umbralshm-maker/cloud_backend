# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from dateutil.parser import isoparse

from .database import SessionLocal, engine
from . import models, schemas, crud
from .security import verify_api_key


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SHM Cloud Backend")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def infer_status(lam: float) -> str:
    if lam is None:
        return "SIN_DATOS"
    if lam < 1.4:
        return "NORMAL"
    if lam < 2.3:
        return "ATENCION"
    if lam < 5.0:
        return "ALERTA"
    return "CRITICO"


@app.post("/ingest/alert")
def ingest_alert(
    data: schemas.AlertIn,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key)
):
    if not data.event_time:
        raise HTTPException(status_code=400, detail="event_time is required")

    try:
        event_time = isoparse(data.event_time)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid event_time format")

    status = data.status or infer_status(data.lambda_max)

    crud.upsert_building(
        db,
        building_id=data.building_id,
        status=status,
        lambda_max=data.lambda_max
    )

    crud.upsert_event(
        db,
        building_id=data.building_id,
        event_id=data.event_id,
        status=status,
        lambda_max=data.lambda_max,
        event_time=event_time
    )

    return {"ok": True}


@app.post("/ingest/report_links")
def ingest_report_links(
    payload: schemas.ReportLinksIn,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key)
):
    try:
        event = crud.get_event(db, payload.event_id)

        if not event:
            crud.upsert_event(
                db,
                building_id=payload.building_id,
                event_id=payload.event_id,
                status="SIN_DATOS",
                lambda_max=None,
                event_time=datetime.utcnow()
            )

        if payload.reports.alerta:
            crud.upsert_report(
                db,
                event_id=payload.event_id,
                rtype="alerta",
                link=payload.reports.alerta.share_link
            )

        if payload.reports.evento:
            crud.upsert_report(
                db,
                event_id=payload.event_id,
                rtype="evento",
                link=payload.reports.evento.share_link
            )

        if payload.reports.mensual:
            crud.upsert_report(
                db,
                event_id=payload.event_id,
                rtype="mensual",
                link=payload.reports.mensual.share_link
            )

        return {"ok": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/buildings", response_model=List[schemas.BuildingOut])
def list_buildings(db: Session = Depends(get_db)):
    return crud.get_all_buildings(db)


@app.get("/buildings/{building_id}", response_model=schemas.BuildingOut)
def get_building(building_id: str, db: Session = Depends(get_db)):
    b = crud.get_building(db, building_id)
    if not b:
        raise HTTPException(status_code=404, detail="Building not found")
    return b


@app.get("/events/{event_id}", response_model=schemas.EventOut)
def get_event(event_id: str, db: Session = Depends(get_db)):
    ev = crud.get_event(db, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return ev


@app.get("/events/{event_id}/reports", response_model=List[schemas.ReportOut])
def get_event_reports(event_id: str, db: Session = Depends(get_db)):
    return crud.get_reports_for_event(db, event_id)
