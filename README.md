# PhishGuard

> Detect phishing URLs instantly using machine learning and AI-powered analysis.

PhishGuard analyzes URLs in real time, extracting 20+ security signals and running them
through a trained classification model to identify phishing attempts. Each scan includes
a plain-English explanation of exactly why a URL is flagged as suspicious.

---

## Features

- **Instant URL analysis** — risk score, verdict, and per-feature breakdown
- **Trained ML model** — Random Forest / XGBoost trained on the UCI Phishing Dataset
- **AI explanations** — Claude API generates a human-readable summary of each result
- **Scan history** — searchable log of all previous scans with filtering by verdict
- **Rate limiting** — API protected against abuse

---

## Tech stack

| Layer      | Technology                            |
| ---------- | ------------------------------------- |
| Frontend   | React 19 + TypeScript + Vite          |
| Backend    | FastAPI (Python)                      |
| ML         | scikit-learn / XGBoost                |
| Database   | SQLite + SQLAlchemy                   |
| AI layer   | Claude API (Anthropic)                |
| Deployment | Railway (backend) · Vercel (frontend) |

---

## Architecture

```
[React Frontend] → [FastAPI Backend] → [Feature Extractor] → [ML Model]
                            ↓
                      [SQLite DB] → [Claude API]
```

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Demo

_Coming soon_

---

## License

MIT
