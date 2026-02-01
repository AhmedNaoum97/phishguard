# Scanner runner
# File scanning logic
# Scanning/Writing: JSON/TXT
# CLI entry point

import json
import argparse
import sys
from scanner import classify


def scan_one(url: str):
    label, severity, score, confidence, reasons = classify(url)
    print(f"[{severity}] {label:15} score={score:2} confidence={confidence:3}% -> {url}")
    return {
        "url": url,
        "label": label,
        "severity": severity,
        "score": score,
        "confidence": confidence,
        "reasons": reasons,
    }


def scan_file(path: str):
    try:
        with open(path, "r") as f:
            urls = [line.split("#")[0].strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{path} not found.")
        return []

    results = []
    for url in urls:
        results.append(scan_one(url))
    return results


def main():
    parser = argparse.ArgumentParser(description="Phishing Guard - Hybrid URL Scanner")
    parser.add_argument("--url", help="Scan a single URL")
    parser.add_argument("--file", default="urls.txt", help="Scan URLs from a file (default: urls.txt)")
    parser.add_argument("--no-interactive", action="store_true", help="Do not prompt for input")

    args = parser.parse_args()

    json_results = []

    # 1) If --url provided, scan it
    if args.url:
        json_results.append(scan_one(args.url))

    # 2) If --file provided (always has a value), scan file
    # Only do this if the user explicitly gave --file OR they gave neither url nor no-interactive
    file_was_explicit = "--file" in sys.argv
    if file_was_explicit or (not args.url and not args.no_interactive):
        json_results.extend(scan_file(args.file))

    # 3) If nothing was scanned and interactive is allowed, prompt
    if not json_results and not args.no_interactive:
        url = input("Enter a URL: ").strip()
        if url:
            json_results.append(scan_one(url))

    # 4) Write outputs if we scanned anything
    if json_results:
        with open("scan_results.json", "w") as jf:
            json.dump(json_results, jf, indent=2)

        with open("scan_results.txt", "w") as out:
            for entry in json_results:
                reasons_text = "; ".join(entry["reasons"])
                message = (
                    f"[{entry['severity']}] {entry['label']}\t"
                    f"score={entry['score']}\tconfidence={entry['confidence']}%\t"
                    f"{entry['url']}\t{reasons_text}"
                )
                out.write(message + "\n")


if __name__ == "__main__":
    main()
