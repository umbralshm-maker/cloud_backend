# -*- coding: utf-8 -*-
"""
Created on Sat Jan 17 13:21:10 2026

@author: ST
"""
# app/security.py
# app/security.py
import os
from fastapi import Header, HTTPException

API_KEY_ENV = "SHM_API_KEY"


def verify_api_key(x_api_key: str = Header(None)):
    expected_key = os.getenv(API_KEY_ENV)

    # Error de configuración del servidor
    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: SHM_API_KEY not set"
        )

    # Petición no autorizada
    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )
