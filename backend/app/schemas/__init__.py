from pydantic import BaseModel
from datetime import datetime


class ScanRequest(BaseModel):
    url: str #


class ScanResponse(BaseModel):
    url: str
    is_phishing: bool
    confidence: float
    scanned_at: datetime


    class Config:
        from_attributes = True