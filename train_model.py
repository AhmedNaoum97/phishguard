# train_model.py
# Training runner for PhishGuard ML model
# Training pipeline


import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

from scanner import extract_features


def label_to_number(label):
    return 1 if label == "LIKELY PHISHING" else 0


def main():
    # 1) Load scan results
    try:
        with open("scan_results.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("scan_results.json not found. Run main.py first.")
        return

    X = []
    y = []
    urls_all = []

    # 2) Build feature matrix and labels
    for entry in data:
        feats = extract_features(entry["url"])
        X.append(list(feats.values()))
        y.append(label_to_number(entry["label"]))
        urls_all.append(entry["url"])

    # Safety check
    if len(X) < 10:
        print("Not enough data to train yet. Add more URLs and re-run scan.")
        return

    # 3) Train / test split
    X_train, X_test, y_train, y_test, urls_train, urls_test = train_test_split(
        X, y, urls_all, test_size=0.3, random_state=42
    )

    # 4) Train model
    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_train, y_train)

    # 5) Evaluate
    preds = model.predict(X_test)
    print(classification_report(y_test, preds))

    probs = model.predict_proba(X_test)[:, 1]
    for url, p in zip(urls_test, probs):
        print(f"{p:.2f} -> {url}")

    # 6) Save model
    joblib.dump(model, "model.pkl")
    print("Saved model to model.pkl")


if __name__ == "__main__":
    main()