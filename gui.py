# gui_app.py
# Simple desktop GUI for Phishing Guard that talks to the FastAPI backend
# Desktop wrapper


import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_BASE = "http://127.0.0.1:8000"


def check_api_health():
    """Ping /health to verify that the API is running."""
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        if r.status_code == 200 and r.json().get("status") == "ok":
            return True
    except requests.RequestException:
        return False
    return False


def scan_url():
    """Send the URL to the FastAPI /scan endpoint and display the result."""
    url = url_var.get().strip()
    if not url:
        messagebox.showwarning("Input required", "Please enter a URL.")
        return

    # Clear previous output
    result_label_var.set("Scanning...")
    details_text.config(state="normal")
    details_text.delete("1.0", tk.END)
    details_text.config(state="disabled")

    try:
        resp = requests.post(f"{API_BASE}/scan", json={"url": url}, timeout=10)
    except requests.RequestException as e:
        messagebox.showerror("Connection error", f"Could not reach API:\n{e}")
        result_label_var.set("Error contacting API")
        return

    if resp.status_code != 200:
        messagebox.showerror(
            "API error",
            f"API returned status {resp.status_code}:\n{resp.text}"
        )
        result_label_var.set("API error")
        return

    data = resp.json()

    label = data.get("label", "UNKNOWN")
    severity = data.get("severity", "UNKNOWN")
    score = data.get("score", "?")
    confidence = data.get("confidence", "?")
    reasons = data.get("reasons", [])

    # Set color based on severity
    color_map = {
        "LOW": "green",
        "MEDIUM": "orange",
        "HIGH": "red",
    }
    color = color_map.get(severity.upper(), "black")

    result_label_var.set(f"{label}  (severity: {severity}, confidence: {confidence}%)")
    result_label.config(foreground=color)

    # Fill details box
    details_text.config(state="normal")
    details_text.delete("1.0", tk.END)

    details_text.insert(tk.END, f"URL: {data.get('url', url)}\n")
    details_text.insert(tk.END, f"Label: {label}\n")
    details_text.insert(tk.END, f"Severity: {severity}\n")
    details_text.insert(tk.END, f"Score: {score}\n")
    details_text.insert(tk.END, f"Confidence: {confidence}%\n\n")

    details_text.insert(tk.END, "Reasons:\n")
    if reasons:
        for r in reasons:
            details_text.insert(tk.END, f"  • {r}\n")
    else:
        details_text.insert(tk.END, "  (No specific reasons)\n")

    details_text.config(state="disabled")


def create_gui():
    global url_var, result_label_var, result_label, details_text

    root = tk.Tk()
    root.title("Phishing Guard - URL Scanner")

    # Main frame
    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # URL input
    ttk.Label(main_frame, text="Enter URL to scan:").grid(
        row=0, column=0, sticky="w"
    )
    url_var = tk.StringVar()
    url_entry = ttk.Entry(main_frame, textvariable=url_var, width=80)
    url_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
    url_entry.focus()

    # Scan button
    scan_button = ttk.Button(main_frame, text="Scan URL", command=scan_url)
    scan_button.grid(row=1, column=2, padx=(8, 0))

    # Result label
    result_label_var = tk.StringVar(value="Ready.")
    result_label = ttk.Label(main_frame, textvariable=result_label_var, font=("Segoe UI", 10, "bold"))
    result_label.grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 5))

    # Details text area
    details_text = tk.Text(main_frame, width=90, height=18, wrap="word")
    details_text.grid(row=3, column=0, columnspan=3, sticky="nsew")
    details_text.config(state="disabled")

    # Scrollbar for text
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=details_text.yview)
    scrollbar.grid(row=3, column=3, sticky="ns")
    details_text.config(yscrollcommand=scrollbar.set)

    # Layout weights
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=0)
    main_frame.columnconfigure(2, weight=0)
    main_frame.rowconfigure(3, weight=1)

    # Check API health once at startup
    if not check_api_health():
        result_label_var.set("Warning: API not reachable at http://127.0.0.1:8000")
        messagebox.showwarning(
            "API not running",
            "Could not reach the FastAPI backend.\n\n"
            "Start it with:\n"
            "  uvicorn api:app --reload"
        )

    root.mainloop()


if __name__ == "__main__":
    create_gui()