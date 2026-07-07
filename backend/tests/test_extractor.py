from app.features.extractor import (
    extract_features,
    to_model_input,
    char_continuation_rate,
    FEATURE_ORDER,
)
import pytest
 
 
def test_is_https_detected():
    features = extract_features("https://example.com")
    assert features["IsHTTPS"] == 1
 
 
def test_http_not_https():
    features = extract_features("http://example.com")
    assert features["IsHTTPS"] == 0
 
 
def test_url_length():
    features = extract_features("https://example.com/login")
    assert features["URLLength"] == 25
 
 
def test_no_of_subdomain():
    features = extract_features("https://sub.example.com/path")
    assert features["NoOfSubDomain"] == 2  # dots in "sub.example.com"
 
 
def test_is_domain_ip():
    features = extract_features("http://192.168.1.1/login")
    assert features["IsDomainIP"] == 1
 
    features = extract_features("https://github.com")
    assert features["IsDomainIP"] == 0
 
 
def test_query_char_counts():
    features = extract_features("https://a.com/p?x=1&y=2&z=3")
    assert features["NoOfQMarkInURL"] == 1
    assert features["NoOfAmpersandInURL"] == 2
 
 
def test_obfuscation_count_and_ratio():
    url = "http://user@evil.com"  # 20 characters, one '@'
    features = extract_features(url)
    assert features["NoOfObfuscatedChar"] == 1
    assert features["ObfuscationRatio"] == pytest.approx(1 / 20)
 
 
def test_digit_and_letter_ratios():
    url = "https://example.com/path123"  # 27 characters, 3 digits, 19 letters
    features = extract_features(url)
    assert features["DegitRatioInURL"] == pytest.approx(3 / 27)
    assert features["LetterRatioInURL"] == pytest.approx(19 / 27)
 
 
def test_char_continuation_rate():
    assert char_continuation_rate("") == 0
    assert char_continuation_rate("abc123") == 1.0
    assert char_continuation_rate("ab-cd") == pytest.approx(2 / 5)
 
 
def test_all_features_present():
    features = extract_features("https://example.com/path?q=1")
    assert set(features.keys()) == set(FEATURE_ORDER)
    assert len(FEATURE_ORDER) == 17
 
 
def test_to_model_input_missing_feature():
    incomplete = {"URLLength": 20}  # everything else missing
    with pytest.raises(ValueError):
        to_model_input(incomplete)
