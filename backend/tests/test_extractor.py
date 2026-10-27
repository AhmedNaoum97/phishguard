from app.features.extractor import (
    FEATURE_ORDER,
    char_continuation_rate,
    extract_features,
    normalize_url,
    to_model_input,
)
import pytest


def test_normalize_url_strips_any_scheme():
    assert normalize_url("https://example.com") == "http://example.com"
    assert normalize_url("HTTP://example.com") == "http://example.com"
    assert normalize_url("example.com") == "http://example.com"
    assert normalize_url("  ftp://example.com  ") == "http://example.com"


def test_scheme_does_not_change_features():
    a = extract_features("https://github.com/AhmedNaoum97")
    b = extract_features("http://github.com/AhmedNaoum97")
    c = extract_features("github.com/AhmedNaoum97")
    assert a == b == c


def test_url_length():
    features = extract_features("https://example.com/login")
    assert features["URLLength"] == len("http://example.com/login")  # 24


def test_no_of_subdomain():
    features = extract_features("https://sub.example.com/path")
    assert features["NoOfSubDomain"] == 2  # dots in "sub.example.com"


def test_is_domain_ip():
    assert extract_features("http://192.168.1.1/login")["IsDomainIP"] == 1
    assert extract_features("https://github.com")["IsDomainIP"] == 0


def test_domain_ignores_port_and_credentials():
    features = extract_features("http://user@evil.com:8080/login")
    assert features["DomainLength"] == len("evil.com")
    assert extract_features("http://192.168.1.1:8080/")["IsDomainIP"] == 1


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
    features = extract_features("https://example.com/path123")
    # normalized to "http://example.com/path123": 26 chars, 3 digits, 18 letters
    assert features["DegitRatioInURL"] == pytest.approx(3 / 26)
    assert features["LetterRatioInURL"] == pytest.approx(18 / 26)


def test_char_continuation_rate():
    assert char_continuation_rate("") == 0
    assert char_continuation_rate("abc123") == 1.0
    assert char_continuation_rate("ab-cd") == pytest.approx(2 / 5)


def test_all_features_present():
    features = extract_features("https://example.com/path?q=1")
    assert set(features.keys()) == set(FEATURE_ORDER)
    assert len(FEATURE_ORDER) == 16


def test_to_model_input_missing_feature():
    with pytest.raises(ValueError):
        to_model_input({"URLLength": 20})