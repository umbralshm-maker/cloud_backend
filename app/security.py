# -*- coding: utf-8 -*-
"""
Created on Sat Jan 17 13:21:10 2026

@author: ST
"""
# app/security.py
import os
from fastapi import Request, HTTPException

API_KEY_ENV = "SHM_API_KEY"
HEADER_NAME = "X-API-Key"


def verify_api_key(request: Request):
    expected_key = os.getenv("SHM_API_KEY")
    received_key = request.headers.get("X-API-Key")

    print("EXPECTED:", repr(expected_key))
    print("RECEIVED:", repr(received_key))

    if not expected_key or received_key != expected_key:
        raise HTTPException(status_code=403, detail="Forbidden")


    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: API key not set"
        )

    received_key = request.headers.get(HEADER_NAME)

    if not received_key or received_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
