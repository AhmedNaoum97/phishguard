# PhishGuard

> Real-time phishing URL analysis using a trained ML classifier — with a documented investigation into why the model fails on real-world traffic, and what that says about URL-only phishing detection.

PhishGuard analyzes URLs in real time, extracting 17 security signals and running them
through a trained classification model. The core value of this project is the
**machine learning investigation**: the model achieves ~100% test accuracy, and this
repository documents exactly why that number is misleading.

---

## Project Status

**Backend and frontend complete. Model retrained and validated (Sprint 2.5 resolved).**
Runs locally — see [Getting started](#getting-started). The model was retrained after a
documented dataset-driven failure — see [Machine Learning Findings](#machine-learning-findings)
and the full [investigation write-up](docs/model-investigation.md).

---

## Progress

- [x] Project setup & FastAPI skeleton
- [x] ML pipeline — data exploration, feature selection, model training & evaluation
- [x] Feature extraction engine (17 URL-only features)
- [x] Backend API & database (`/api/predict`, `/api/scans`, SQLite persistence)
- [x] Root-cause investigation of real-world false positives (see ML Findings)
- [x] Test suite — pytest, 13 tests (feature extractor unit tests + API contract tests)
- [x] Frontend — scan form wired to `/api/predict` (React + TypeScript + Vite)
- [x] Frontend — recent scans list via `/api/scans`
- [x] Model retrain — augmented legitimate class with realistic deep URLs (Sprint 2.5)

### Future work (deliberately deprioritized)

- Layer in domain reputation / age / threat-intel signals — URL shape alone has a signal ceiling
- AI explanation layer (Claude API)
- Public deployment

---

## Features

- **Instant URL analysis** — risk score, verdict, and per-feature breakdown via `/api/predict`
- **Scan form UI** — React frontend with typed API responses, loading state, and input guards
- **Trained ML model** — Random Forest / XGBoost trained on the PhiUSIIL Phishing URL Dataset (2024)
- **Scan history** — persistent log of the 50 most recent scans via `/api/scans`

---

## Tech stack

| Layer    | Technology                |
| -------- | ------------------------- |
| Frontend | React + TypeScript (Vite) |
| Backend  | FastAPI (Python)          |
| ML       | scikit-learn / XGBoost    |
| Database | SQLite + SQLAlchemy       |

Public deployment is not set up yet — see [Future work](#progress). The deployment
skillset is demonstrated in
[SafeNet Companion](https://github.com/AhmedNaoum97/safenet-companion).

---

## Architecture

```
[React Frontend] → [FastAPI Backend] → [Feature Extractor] → [ML Model]
                         ↓
                    [SQLite DB]
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

This points to a known limitation of academic phishing datasets: legitimate and phishing URLs are typically sourced very differently, making them structurally easy to separate.

**Update (Sprint 3): this limitation was confirmed in production.** Once the live feature extractor and `/api/predict` endpoint were built, real-world URLs were tested against the model. Every URL — including obviously legitimate ones like `github.com`, `google.com/search`, and `wikipedia.org` — was flagged as phishing (confidence 0.61–0.99).

Root-cause investigation traced this to the dataset's _legitimate_ class: sampling the `label == 1` rows revealed they are almost entirely bare homepages (`https://www.example.com` with no path or query string), while the phishing class contains full URLs with paths and parameters. The model therefore learned a shortcut — "any URL with a path is phishing" — which perfectly separates this dataset (hence 100% test accuracy) but fails completely on real traffic, where legitimate URLs routinely have paths.

This is a textbook **train/serve distribution mismatch**.

**Update (Sprint 2.5): fixed and validated.** The model was retrained on the
[`malicious_phish`](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset)
dataset, where legitimate URLs include realistic paths and query strings, using the
same `extractor.py` module the live API imports — eliminating the possibility of
train/serve drift by construction. Two further bugs were caught and fixed during the
retrain: a stale feature set left over from a prior extractor change, and an inverted
label convention that was only caught by testing the _deployed_ `/api/predict` endpoint
directly, not just the training notebook's own metrics.

**Results:** 89% held-out test accuracy (down from v1's misleading ~100% — the honest,
expected outcome), 86.3% of PhiUSIIL's phishing URLs correctly caught as an
out-of-distribution generalization check, and `github.com/AhmedNaoum97` — the exact case
that broke v1 — now correctly classified as legitimate, confirmed live through the
deployed API.

This remains a **single-signal, URL-only detector** — it has no domain reputation, age,
or threat-intel layer, and should not be treated as production-ready security software.
That ceiling is why a follow-up project layering in those signals is the natural next
step. Full investigation write-up, including the retrain and both bugs found along the
way: [`docs/model-investigation.md`](docs/model-investigation.md).

---

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 20+

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

Open http://localhost:5173 — the backend must be running on port 8000.

### Run the tests

```bash
cd backend
python -m pytest
```

---

## Demo (local)

Run the backend and frontend (see [Getting started](#getting-started)), then scan a URL
in the UI:

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/AhmedNaoum97"}'
```

```json
{
  "url": "https://github.com/AhmedNaoum97",
  "is_phishing": false,
  "confidence": 0.965,
  "scanned_at": "2026-09-09T02:47:58.965334"
}
```

This is the exact URL that the pre-retrain model (v1) incorrectly flagged as phishing
— see [ML Findings](#machine-learning-findings) for the full before/after story.

Public deployment isn't set up yet; see [Future work](#progress).

---

## License

MIT
