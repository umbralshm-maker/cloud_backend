# app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from .database import SessionLocal, engine
from . import models, schemas, crud
from typing import List
from fastapi import HTTPException

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
def ingest_alert(data: schemas.AlertIn, db: Session = Depends(get_db)):
    status = data.status or infer_status(data.lambda_max)

    crud.upsert_building(
        db,
        building_id=data.building_id,
        status=status,
        lambda_max=data.lambda_max
    )

    crud.create_event(
        db,
        building_id=data.building_id,
        event_id=data.event_id,
        status=status,
        lambda_max=data.lambda_max,
        event_time=datetime.fromisoformat(data.event_time) if data.event_time else None
    )

    return {"ok": True}


@app.post("/ingest/report_links")
def ingest_report_links(data: schemas.ReportLinksIn, db: Session = Depends(get_db)):
    for rtype, payload in data.reports.items():
        crud.upsert_report(
            db,
            event_id=data.event_id,
            rtype=rtype,
            link=payload["share_link"]
        )
    return {"ok": True}



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
