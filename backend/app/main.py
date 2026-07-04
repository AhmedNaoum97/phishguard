from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json

from .schemas import ScanRequest, ScanResponse
from .models import Scan
from .core.database import get_db
from .services.predictor import predict_phishing

app = FastAPI(
    title="PhishGuard API",
    description="AI-powered phishing URL detection",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "phishguard-api"}

@app.post("/api/predict", response_model=ScanResponse)
def predict(request: ScanRequest, db: Session = Depends(get_db)):
    result = predict_phishing(request.url)
    scan = Scan(
        url=result["url"],
        is_phishing=result["is_phishing"],
        confidence=result["confidence"],
        features=json.dumps(result["features"]),
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan

@app.get("/api/scans", response_model=list[ScanResponse])
def get_scans(db: Session = Depends(get_db)):
    scans = db.query(Scan).order_by(Scan.scanned_at.desc()).limit(50).all()
    return scans