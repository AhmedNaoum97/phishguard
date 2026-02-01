# Phishing Guard - Hybrid Phishing URL Detector

Phishing Guard combines rule-based heuristics and machine learning
to detect phishing URLs with both explainability and automation.
The project is designed similar to how SOC tools analyze suspicious domains.

---

## Features

### Rule-Based Detection
Detects common phishing indicators:
- Suspicious keywords (login, verify, account, secure, bank)
- Risky TLDs (.ru, .tk, .zip, .xyz, .top)
- Missing HTTPS
- Too many subdomains or dots
- Special characters (@ or -)
- Very long URLs

Every classification includes a readable explanation.

---

## Batch Scanning Pipeline

Supports scanning through:
- Single URL input
- Batch scan using urls.txt

Outputs:
- scan_results.txt (human readable)
- scan_results.json (machine readable for ML)

---

## Feature Engineering for ML

URLs are transformed into numeric features including:
- URL length
- Path length
- Query length
- Subdomain count
- Digit count
- HTTPS usage
- Risky TLD detection
- IP address in URL
- Phishing keyword presence

---

## Machine Learning Component

- Binary classification (Phishing vs Legitimate)
- Logistic Regression
- Class imbalance handled using class_weight="balanced"

Outputs:
- Precision, Recall, F1-score
- Probability score per URL

Example:
0.94 -> http://account-locked.example.zip
0.01 -> https://www.google.com

ML is optional: rule-based results still work without model.pkl.

---

## Evaluation Metrics

- Accuracy
- Precision / Recall / F1-score
- Prioritizes high recall to reduce missed phishing attacks

---

## Explainability

Phishing Guard combines:
1. Rule-based explanation: what triggered suspicion
2. ML probability: how likely the URL is phishing

This makes it suitable for learning, security analysis, and SOC workflows.

---

## Project Structure

phishguard/
  main.py              - CLI scanner (rules + logging)
  scanner.py           - Core feature extraction and scoring
  train_model.py       - Train ML model using scan_results.json
  predict.py           - Predict phishing probability with trained model
  api.py               - REST API with FastAPI
  gui.py               - Tkinter desktop application
  urls.txt             - Input file for batch scanning
  scan_results.txt     - Human readable logging output
  scan_results.json    - JSON results, used for ML
  model.pkl            - Trained model file (after training)
  .gitignore
  README.md

---

## Usage

Step 1: Install dependencies
pip install -r requirements.txt

Step 2: Run scanner (rule-based)
python main.py

Step 3: Train the machine learning model
python train_model.py

Step 4: Predict using saved model
python predict.py

Step 5: Start API
uvicorn api:app --reload

Step 6: Run GUI
python gui.py

---

## API

POST /scan
Body: { "url": "http://phishing-example.ru" }

Returns JSON:
- label
- probability
- rule-based reasons

---

## GUI

The Tkinter GUI sends URLs to the backend and displays:
- Classification result
- ML probability
- Evidence from rules

---

## Future Improvements

- Train on PhishTank or OpenPhish datasets
- Add ROC-AUC and confusion matrix
- Try RandomForest / XGBoost
- Deploy API to Render / Railway
- Add full web dashboard

---

## Skills Demonstrated

- Python scripting
- Defensive programming
- FastAPI + REST APIs
- Tkinter GUI development
- Feature engineering
- Machine learning classification
- Model evaluation (precision, recall, F1)
- Explainable AI
- Project structuring and version control

---


## How to run
# Start backend
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000

# In a new terminal, start GUI
python gui.py

# Test backend
http://127.0.0.1:8000/docs


## Author

Built as a cybersecurity and machine learning portfolio project  
by Ahmed Naoum - Gokstad Akademiet
