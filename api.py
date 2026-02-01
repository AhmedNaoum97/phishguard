# api.py
# FastAPI service for Phishing Guard
# HTTP layer

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import joblib

from scanner import classify, extract_features



app = FastAPI(title="Phishing Guard API")

class URLRequest(BaseModel):
    url: str


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/scan")
def scan_url(body: URLRequest):
    label, severity, score, confidence, reasons = classify(body.url)
    return {
        "url": body.url,
        "label": label,
        "severity": severity,
        "score": score,
        "confidence": confidence,
        "reasons": reasons,
    }

@app.get("/")
def root():
    return {"message": "Phishing Guard API is running. See /docs for usage."}
