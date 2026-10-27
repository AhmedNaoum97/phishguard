import json
import re
from pathlib import Path
from urllib.parse import urlparse

FEATURE_ORDER = [
    'URLLength', 'DomainLength', 'IsDomainIP', 'CharContinuationRate',
    'TLDLegitimateProb', 'URLCharProb', 'TLDLength', 'NoOfSubDomain',
    'NoOfObfuscatedChar', 'ObfuscationRatio', 'LetterRatioInURL',
    'DegitRatioInURL', 'NoOfQMarkInURL', 'NoOfAmpersandInURL',
    'NoOfOtherSpecialCharsInURL', 'SpacialCharRatioInURL',
]

_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")

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


def normalize_url(url: str) -> str:
    """Strip any scheme and prefix http:// so training and serving see identical input."""
    return "http://" + _SCHEME.sub("", url.strip())


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
    url = normalize_url(url)
    parsed = urlparse(url)
    # hostname excludes port and user@ credentials, and is lowercased
    domain = parsed.hostname or ""
    url_len = len(url)

    features = {}
    features['URLLength'] = url_len
    features['NoOfQMarkInURL'] = url.count('?')
    features['NoOfAmpersandInURL'] = url.count('&')

    features['DomainLength'] = len(domain)
    tld = domain.split('.')[-1] if '.' in domain else domain
    features['TLDLength'] = len(tld)
    features['NoOfSubDomain'] = domain.count('.')
    features['IsDomainIP'] = 1 if all(part.isdigit() for part in domain.split('.')) else 0

    digit_count = sum(1 for c in url if c.isdigit())
    letter_count = sum(1 for c in url if c.isalpha())
    features['DegitRatioInURL'] = digit_count / url_len
    features['LetterRatioInURL'] = letter_count / url_len

    features['NoOfObfuscatedChar'] = url.count('@')
    features['ObfuscationRatio'] = features['NoOfObfuscatedChar'] / url_len
    features['NoOfOtherSpecialCharsInURL'] = sum(url.count(c) for c in ('-', '_'))
    features['SpacialCharRatioInURL'] = (
        features['NoOfOtherSpecialCharsInURL'] + features['NoOfObfuscatedChar']
    ) / url_len

    features['CharContinuationRate'] = char_continuation_rate(url)
    features['TLDLegitimateProb'] = _tld_probs.get(tld, 0.0)
    char_scores = [_char_probs.get(c, 0.0) for c in url]
    features['URLCharProb'] = sum(char_scores) / len(char_scores)
    return features


def to_model_input(features: dict) -> list:
    try:
        return [features[name] for name in FEATURE_ORDER]
    except KeyError as e:
        raise ValueError(f"Missing feature: {e}")