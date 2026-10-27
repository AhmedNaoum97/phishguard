# PhishGuard

> Real-time phishing URL analysis with a trained ML classifier — and a documented investigation into why the first model failed on real-world traffic, how it was fixed, and what that says about URL-only phishing detection.

PhishGuard analyzes URLs in real time, extracting 16 URL-based security signals and running
them through a Random Forest classifier. The core value of this project is the
**machine learning investigation**: v1 scored ~100% test accuracy and failed completely on
real traffic. This repository documents why, how it was diagnosed, and how it was fixed.

---

## Project Status

**Backend and frontend complete. Model retrained and validated.** Runs locally — see
[Getting started](#getting-started). See [Machine Learning Findings](#machine-learning-findings)
and the full [investigation write-up](docs/model-investigation.md).

---

## Progress

- [x] Project setup & FastAPI skeleton
- [x] ML pipeline — data exploration, feature selection, model training & evaluation
- [x] Feature extraction engine (16 URL-only features)
- [x] Backend API & database (`/api/predict`, `/api/scans`, SQLite persistence)
- [x] Root-cause investigation of real-world false positives (see ML Findings)
- [x] Frontend — scan form and recent scans list (React + TypeScript + Vite)
- [x] Model retrain on a dataset with realistic legitimate URLs (Sprint 2.5)
- [x] Train/serve skew fix — URL normalization moved into the shared extractor, model retrained and compressed (290.8 MB → 19.6 MB)
- [x] Test suite — pytest, 14 tests (extractor unit tests, regression test for the skew fix, API contract tests)

### Future work

- Input validation on `/api/predict` (length cap, scheme allowlist)
- CI pipeline (GitHub Actions) running the test suite on every push
- Layer in domain reputation / age / threat-intel signals — URL shape alone has a signal ceiling
- Public deployment

---

## Features

- **Instant URL analysis** — phishing verdict and confidence via `/api/predict`
- **Scan form UI** — React frontend with typed API responses, loading state, and error handling
- **Trained ML model** — Random Forest trained on the `malicious_phish` dataset, validated out-of-distribution on PhiUSIIL
- **Scan history** — persistent log of the 50 most recent scans via `/api/scans`

---

## Tech stack

| Layer    | Technology                       |
| -------- | -------------------------------- |
| Frontend | React + TypeScript (Vite)        |
| Backend  | FastAPI (Python)                 |
| ML       | scikit-learn 1.8 (Random Forest) |
| Database | SQLite + SQLAlchemy              |

Public deployment is not set up yet — see [Future work](#future-work). The deployment
skillset is demonstrated in
[SafeNet Companion](https://github.com/AhmedNaoum97/safenet-companion).

---

## Architecture

```
[React Frontend] → [FastAPI Backend] → [Feature Extractor] → [ML Model]
                         ↓
                    [SQLite DB]
```

The same `extractor.py` module is imported by both the training notebook and the API, so
training and serving compute features identically.

---

## Machine Learning Findings

### v1: a perfect score that failed in production

v1 was trained on the [PhiUSIIL Phishing URL Dataset](https://www.kaggle.com/datasets/ndarvind/phiusiil-phishing-url-dataset)
(2024, peer-reviewed, 235,795 URLs). Random Forest and XGBoost both scored ~100% accuracy.
Leakage checks came back clean (highest feature–label correlation 0.86, 0.34% duplicates),
and a deliberately simple Logistic Regression also scored 99.99% — pointing at the data,
not the model.

Once the live `/api/predict` endpoint was built, **every** real URL — including
`github.com`, `google.com/search`, and `wikipedia.org` — was flagged as phishing.
Root cause: the dataset's legitimate class was almost entirely bare homepages, while the
phishing class had full paths. The model learned the shortcut "has a path = phishing" —
a textbook **train/serve distribution mismatch**.

### Sprint 2.5: retrain on realistic data

The model was retrained on the
[`malicious_phish`](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset)
dataset, where legitimate URLs include realistic paths and query strings, with features
computed by the same extractor the API uses. Two bugs were caught along the way: a stale
feature set from a prior extractor change, and an inverted label convention found only by
testing the deployed endpoint, not the notebook's own metrics.

### Train/serve skew fix

A later code review found a remaining skew: the notebook stripped `http(s)://` before
extraction, but the API did not — so 5 of 16 features differed between training and
serving. Scheme normalization was moved **inside** `extract_features`, so both paths now
receive identical input by construction, and a regression test asserts that
`https://`, `http://`, and scheme-less URLs produce identical features. Domain features
now use `hostname` instead of `netloc`, so ports and `user@` credentials no longer distort
them. The model was retrained on the corrected features and compressed from 290.8 MB to
19.6 MB, so it ships with the repository.

### Results

| Metric                                              | v1                 | Current   |
| --------------------------------------------------- | ------------------ | --------- |
| Held-out test accuracy                              | ~100% (misleading) | **89%**   |
| PhiUSIIL phishing URLs caught (out-of-distribution) | —                  | **88.7%** |
| Legitimate sanity set (5 real URLs)                 | 0/5                | **5/5**   |
| Model file size                                     | —                  | 19.6 MB   |

This remains a **single-signal, URL-only detector** — no domain reputation, age, or
threat-intel layer — and should not be treated as production-ready security software.
Full write-up: [`docs/model-investigation.md`](docs/model-investigation.md).

---

## Getting started

### Prerequisites

- Python 3.11 (the model was serialized with scikit-learn 1.8.0 on Python 3.11)
- Node.js 20+

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
copy .env.example .env         # macOS/Linux: cp .env.example .env
python init_db.py
python -m uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the backend must be running on port 8000.

### Run the tests

```bash
cd backend
python -m pytest
```

---

## Demo (local)

With the backend running:

```bash
# macOS/Linux
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/AhmedNaoum97"}'

# Windows PowerShell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/predict -ContentType "application/json" -Body '{"url": "https://github.com/AhmedNaoum97"}' | ConvertTo-Json
```

```json
{
  "url": "https://github.com/AhmedNaoum97",
  "is_phishing": false,
  "confidence": 0.9400109328974132,
  "scanned_at": "2026-10-27T16:39:26.571906"
}
```

This is the exact URL that v1 incorrectly flagged as phishing.

---

## License

MIT
