# PhishGuard

> Real-time phishing URL analysis using a trained ML classifier — with a documented investigation into why the model fails on real-world traffic, and what that says about URL-only phishing detection.

PhishGuard analyzes URLs in real time, extracting 17 security signals and running them
through a trained classification model. The core value of this project is the
**machine learning investigation**: the model achieves ~100% test accuracy, and this
repository documents exactly why that number is misleading.

---

## Project Status

**Backend complete. Frontend in progress (Sprint 4).** Runs locally — see
[Getting started](#getting-started). The trained model carries a documented
dataset-driven limitation — see [Machine Learning Findings](#machine-learning-findings).
Model retrain is scoped as Sprint 2.5; the frontend renders whatever the API returns,
so it is unaffected by the retrain.

---

## Progress

- [x] Project setup & FastAPI skeleton
- [x] ML pipeline — data exploration, feature selection, model training & evaluation
- [x] Feature extraction engine (17 URL-only features)
- [x] Backend API & database (`/api/predict`, `/api/scans`, SQLite persistence)
- [x] Root-cause investigation of real-world false positives (see ML Findings)
- [x] Test suite — pytest, 13 tests (feature extractor unit tests + API contract tests)
- [x] Frontend — scan form wired to `/api/predict` (React + TypeScript + Vite)
- [ ] Frontend — recent scans list via `/api/scans` (in progress)

### Future work (deliberately deprioritized)

- Model retrain — augment the legitimate class with realistic deep URLs (scoped as Sprint 2.5)
- AI explanation layer (Claude API)

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

Public deployment is intentionally skipped until the Sprint 2.5 retrain — knowingly
serving invalid verdicts adds nothing. The deployment skillset is demonstrated in
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

This is a textbook **train/serve distribution mismatch**. The fix is documented as future work (Sprint 2.5): augment the legitimate class with realistic URLs containing paths and query strings, retrain, and validate against a fixed real-world benchmark set rather than only the dataset's own test split. It was deliberately deprioritized — the investigation itself is the core finding of this project, and URL-only classification has a signal ceiling regardless of training data. Production phishing detection layers in domain reputation, domain age, and threat intelligence, which is the approach explored in the follow-up project. Full investigation write-up: [`docs/model-investigation.md`](docs/model-investigation.md).

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
in the UI — and note the false positive. That's the point (see
[ML Findings](#machine-learning-findings)):

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/AhmedNaoum97"}'
```

```json
{
  "url": "https://github.com/AhmedNaoum97",
  "is_phishing": true,
  "confidence": 0.61,
  "scanned_at": "2026-07-07T14:47:58.965334"
}
```

Public deployment is intentionally skipped until the Sprint 2.5 retrain — the model's
documented validity issue means there is no value in serving it publicly yet.

---

## License

MIT
