from pathlib import Path

import joblib

from ..features.extractor import extract_features, to_model_input

PHISHING = 1  # training label convention: 1 = phishing, 0 = legitimate

_model_path = Path(__file__).parent.parent / "ml" / "phishguard_model_url_only.pkl"
_model = joblib.load(_model_path)  # loaded once, at import
_phishing_index = list(_model.classes_).index(PHISHING)


def predict_phishing(url: str) -> dict:
    features = extract_features(url)
    proba = _model.predict_proba([to_model_input(features)])[0]
    phishing_proba = float(proba[_phishing_index])
    is_phishing = phishing_proba >= 0.5

    return {
        "url": url,
        "is_phishing": is_phishing,
        "confidence": phishing_proba if is_phishing else 1 - phishing_proba,
        "features": features,
    }