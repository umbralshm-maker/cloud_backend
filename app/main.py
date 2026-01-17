# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from dateutil.parser import isoparse
import os

from .database import SessionLocal, engine
from . import models, schemas, crud


# =========================
# DB init
# =========================
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SHM Cloud Backend")


# =========================
# Dependencies
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_api_key(x_api_key: str = Header(None)):
    """
    Seguridad por API KEY.
    - La key DEBE existir en Render como SHM_API_KEY
    - El cliente DEBE enviarla como header X-API-Key
    """
    expected = os.getenv("SHM_API_KEY")

    if not expected:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: SHM_API_KEY not set"
        )

    if x_api_key != expected:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )


# =========================
# Utils
# =========================
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


# =========================
# INGESTA
# =========================
@app.post("/ingest/alert", dependencies=[Depends(verify_api_key)])
def ingest_alert(
    data: schemas.AlertIn,
    db: Session = Depends(get_db),
):
    if not data.event_time:
        raise HTTPException(
            status_code=400,
            detail="event_time is required"
        )

    try:
        event_time = isoparse(data.event_time)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid event_time format"
        )

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
        event = crud.get_event(
            db,
            payload.building_id,
            payload.event_id
        )

        if not event:
            event = crud.create_placeholder_event(
                db,
                payload.building_id,
                payload.event_id
            )

        if payload.reports.alerta:
            crud.upsert_report(
                db,
                payload.building_id,
                payload.event_id,
                "alerta",
                payload.reports.alerta.share_link
            )

        if payload.reports.evento:
            crud.upsert_report(
                db,
                payload.building_id,
                payload.event_id,
                "evento",
                payload.reports.evento.share_link
            )

        if payload.reports.mensual:
            crud.upsert_report(
                db,
                payload.building_id,
                payload.event_id,
                "mensual",
                payload.reports.mensual.share_link
            )

        return {"ok": True}

    except Exception as e:
        print("🔥 EXCEPTION:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# QUERIES
# =========================
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


@app.get(
    "/buildings/{building_id}/events/{event_id}/reports",
    response_model=List[schemas.ReportOut]
)
def get_event_reports(
    building_id: str,
    event_id: str,
    db: Session = Depends(get_db)
):
    return crud.get_reports_for_event(db, building_id, event_id)