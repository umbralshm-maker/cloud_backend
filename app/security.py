# -*- coding: utf-8 -*-
"""
Created on Sat Jan 17 13:21:10 2026

@author: ST
"""
# app/security.py
import os
from fastapi import Header, HTTPException

def verify_api_key(x_api_key: str = Header(None)):
    server_key = os.getenv("SHM_API_KEY")

    # modo desarrollo sin key (opcional)
    if not server_key:
        return

    if x_api_key != server_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )