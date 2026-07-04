from urllib.parse import urlparse
import json
from pathlib import Path

FEATURE_ORDER = [
    'URLLength', 'DomainLength', 'IsDomainIP', 'CharContinuationRate',
    'TLDLegitimateProb', 'URLCharProb', 'TLDLength', 'NoOfSubDomain',
    'NoOfObfuscatedChar', 'ObfuscationRatio', 'LetterRatioInURL',
    'DegitRatioInURL', 'NoOfQMarkInURL', 'NoOfAmpersandInURL',
    'NoOfOtherSpecialCharsInURL', 'SpacialCharRatioInURL', 'IsHTTPS'
]

_tld_probs = None
_char_probs = None

def _load_probs():
    global _tld_probs, _char_probs
    if _tld_probs is None:
        base_path = Path(__file__).parent.parent / 'ml'
        with open(base_path / 'tld_probs.json') as f:
            _tld_probs = json.load(f)
        with open(base_path / 'char_probs.json') as f:
            _char_probs = json.load(f)

def char_continuation_rate(url: str) -> float:
    max_run = 0
    current_run = 0
    for c in url:
        if c.isalnum():
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0
    return max_run / len(url) if len(url) > 0 else 0

def extract_features(url: str) -> dict:
    _load_probs()
    parsed = urlparse(url)
    features = {}
    features['URLLength'] = len(url)
    features['IsHTTPS'] = 1 if parsed.scheme == 'https' else 0
    features['NoOfQMarkInURL'] = url.count('?')
    features['NoOfAmpersandInURL'] = url.count('&')
    domain = parsed.netloc
    features['DomainLength'] = len(domain)
    features['TLDLength'] = len(domain.split('.')[-1]) if '.' in domain else len(domain)
    features['NoOfSubDomain'] = domain.count('.')
    parts = domain.split('.')
    features['IsDomainIP'] = 1 if all(part.isdigit() for part in parts) else 0
    digit_count = sum(1 for c in url if c.isdigit())
    letter_count = sum(1 for c in url if c.isalpha())
    url_len = len(url) if len(url) > 0 else 1
    features['DegitRatioInURL'] = digit_count / url_len
    features['LetterRatioInURL'] = letter_count / url_len
    features['NoOfObfuscatedChar'] = url.count('@')
    special_chars = ['-', '_']
    features['NoOfOtherSpecialCharsInURL'] = sum(url.count(c) for c in special_chars)
    features['CharContinuationRate'] = char_continuation_rate(url)
    tld = domain.split('.')[-1] if '.' in domain else domain
    features['TLDLegitimateProb'] = _tld_probs.get(tld, 0.0)
    char_scores = [_char_probs.get(c, 0.0) for c in url]
    features['URLCharProb'] = sum(char_scores) / len(char_scores) if char_scores else 0.0
    features['ObfuscationRatio'] = features['NoOfObfuscatedChar'] / url_len
    features['SpacialCharRatioInURL'] = (features['NoOfOtherSpecialCharsInURL'] + features['NoOfObfuscatedChar']) / url_len
    return features

def to_model_input(features: dict) -> list:
    try:
        return [features[name] for name in FEATURE_ORDER]
    except KeyError as e:
        raise ValueError(f"Missing feature: {e}")
