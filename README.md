# PhishGuard

> Detect phishing URLs instantly using machine learning and AI-powered analysis.

PhishGuard analyzes URLs in real time, extracting 20+ security signals and running them
through a trained classification model to identify phishing attempts. Each scan includes
a plain-English explanation of exactly why a URL is flagged as suspicious.

---

## Project Status

🚧 In active development. See [progress below](#progress) for what's built vs. in progress.

---

## Progress

- [x] Project setup & FastAPI skeleton
- [x] ML pipeline — data exploration, feature selection, model training & evaluation
- [ ] Feature extraction engine
- [ ] Backend API & database
- [ ] Frontend
- [ ] AI explanation layer (Claude API)
- [ ] Deployment

---

## Features

- **Instant URL analysis** — risk score, verdict, and per-feature breakdown
- **Trained ML model** — Random Forest / XGBoost trained on the PhiUSIIL Phishing URL Dataset (2024)
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

---

## Machine Learning Findings

The model was trained and evaluated on the [PhiUSIIL Phishing URL Dataset](https://www.kaggle.com/datasets/ndarvind/phiusiil-phishing-url-dataset) (2024, peer-reviewed) — 235,795 URLs labeled phishing or legitimate.

**Approach:**

1. Explored 55 raw features, dropped 5 redundant/low-value columns based on correlation analysis and Random Forest feature importance
2. Trained and compared two models with 5-fold cross-validation: Random Forest and XGBoost
3. Evaluated using precision, recall, F1, confusion matrix, and ROC-AUC — not just accuracy
4. Selected **Random Forest** as the final model (performs identically to XGBoost here, but simpler to explain and has no extra inference-time dependency)

**A note on near-perfect accuracy:**
Both models scored ~100% accuracy, which initially looked suspicious. Investigated for data leakage — checked feature correlation with the label (highest: 0.86, not high enough to explain this) and duplicate rows (0.34%, too small to explain this). Confirmed with a deliberately simple Logistic Regression model, which also scored 99.99%.

This points to a known limitation of academic phishing datasets: legitimate and phishing URLs are typically sourced very differently (top-traffic lists vs. threat-intelligence feeds), making them structurally easy to separate. This doesn't reflect how the model would perform against real-world phishing that actively mimics legitimate sites — a limitation worth keeping in mind as this project moves toward a live feature extractor in Sprint 2.

---

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
