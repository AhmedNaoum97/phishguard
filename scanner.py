# scanner.py
# Rules + Features
# Logic + features

from urllib.parse import urlparse

def risk_score(url):
    score = 0
    reasons = []
    lower_url = url.lower()

    parsed_url = urlparse(lower_url)
    domain = parsed_url.netloc

    if domain == "":
        domain = lower_url.split("/")[0]

    trusted_domains = [
        "google.com", "accounts.google.com",
        "microsoft.com", "login.microsoftonline.com",
        "apple.com", "icloud.com",
        "github.com"
    ]

    for td in trusted_domains:
        if domain == td or domain.endswith("." + td):
            return 0, ["Trusted domain"]

    if len(lower_url) > 60:
        score += 2
        reasons.append("Long URL")

    if len(lower_url) > 100:
        score += 2
        reasons.append("Very long URL")

    if "@" in lower_url:
        score += 4
        reasons.append("Contains @")

    if "-" in domain:
        score += 1
        reasons.append("Dash in domain")

    if domain.count(".") >= 4:
        score += 2
        reasons.append("Many subdomains")

    if not lower_url.startswith("https://"):
        score += 1
        reasons.append("Not using HTTPS")

    phishing_words = ["login", "verify", "update", "secure", "account", "password", "bank"]
    for word in phishing_words:
        if word in lower_url:
            score += 2
            reasons.append(f"Contains phishing word: {word}")

    risky_tlds = [".ru", ".tk", ".zip", ".top", ".xyz"]
    for tld in risky_tlds:
        if domain.endswith(tld):
            score += 2
            reasons.append(f"Risky TLD: {tld}")

    return score, reasons


def classify(url):
    """
    Classify a URL using rule-based scoring

    Returns:
        (label, severity, score, confidence, reasons)
    """
    score, reasons = risk_score(url)

    confidence = min(100, score * 15)

    if score >= 8:
        label = "LIKELY PHISHING"
        severity = "HIGH"
    elif score >= 4:
        label = "SUSPICIOUS"
        severity = "MEDIUM"
    else:
        label = "LIKELY SAFE"
        severity = "LOW"

    return label, severity, score, confidence, reasons


def extract_features(url):
    lower_url = url.lower()
    parsed = urlparse(lower_url)
    domain = parsed.netloc if parsed.netloc else lower_url.split("/")[0]
    domain = domain.split(":")[0]  # Remove port if present

    features = {
        "length": len(lower_url),
        "dot_count": domain.count("."),
        "has_at": 1 if "@" in lower_url else 0,
        "has_dash": 1 if "-" in domain else 0,
        "has_https": 1 if lower_url.startswith("https://") else 0,
        "risky_tld": 1 if domain.endswith((".ru", ".tk", ".zip", ".top", ".xyz")) else 0,
        "phishing_word": 1 if any(w in lower_url for w in [
            "login", "verify", "update", "secure", "password", "bank", "account"
        ]) else 0,

        # NEW FEATURES
        "path_length": len(parsed.path),
        "query_length": len(parsed.query),
        "num_digits": sum(c.isdigit() for c in lower_url),
        "subdomain_count": max(0, domain.count(".") - 1),
        "has_ip": 1 if (
            domain.replace(".", "").isdigit() and
            domain.count(".") == 3 and
            all(0 <= int(part) <= 255 for part in domain.split("."))
        ) else 0,
    }

    return features