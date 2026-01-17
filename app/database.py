# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 23:46:31 2026

@author: ST
"""

# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


DB_PATH = os.environ.get("DB_PATH", "/data/shm.db")
DATABASE_URL = os.environ["DATABASE_URL"]


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
