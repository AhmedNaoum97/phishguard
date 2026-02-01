# predict.py
# Use saved model on new URL
# Prediction runner
# Inference

import joblib
from scanner import extract_features



def main():
    # 1) Load model
    try:
        model = joblib.load("model.pkl")
    except FileNotFoundError:
        print("model.pkl not found. Run train_model.py first.")
        return

    # 2) Ask for a URL
    url = input("Enter a URL to predict: ").strip()
    if url == "":
        print("No URL entered.")
        return

    # 3) Extract features (same feature order as training)
    feats = extract_features(url)
    X_one = [list(feats.values())]  # model expects 2D: [ [features...] ]

    # 4) Predict probability (class 1 = phishing)
    prob_phish = model.predict_proba(X_one)[0][1]

    # 5) Decide label using a threshold
    threshold = 0.50
    label = "LIKELY PHISHING" if prob_phish >= threshold else "LIKELY SAFE"

    # 6) Print results
    print(f"Prediction: {label}")
    print(f"Phishing probability: {prob_phish:.2f}")


if __name__ == "__main__":
    main()
