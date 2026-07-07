import joblib
from pathlib import Path
from ..features.extractor import extract_features, to_model_input

_model_path = Path(__file__).parent.parent / 'ml' / 'phishguard_model_url_only.pkl'
_model = joblib.load(_model_path)  # loaded once, when this module first imports

def predict_phishing(url: str) -> dict:
    features = extract_features(url)
    model_input = to_model_input(features)

    pred_proba = _model.predict_proba([model_input])[0]
    pred_class = _model.predict([model_input])[0]

    return {
        "url": url,
        "is_phishing": bool(pred_class == 0),
        "confidence": float(max(pred_proba)),
        "features": features,
    }