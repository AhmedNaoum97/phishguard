import { useState, useEffect } from "react";

type ScanResult = {
  url: string;
  is_phishing: boolean;
  confidence: number;
  scanned_at: string;
};

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<ScanResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [recentScans, setRecentScans] = useState<ScanResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadScans() {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/scans");
      if (!response.ok) {
        throw new Error("Failed to fetch scan results");
      }
      const data: ScanResult[] = await response.json();
      setRecentScans(data);
    } catch {
      setError("Could not fetch recent scans.");
    }
  }

  useEffect(() => {
    loadScans();
  }, []);

  async function handleScan() {
    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url }),
      });

      const data: ScanResult = await response.json();
      setResult(data);
      await loadScans();
    } catch {
      setError("Could not reach the scanner. Is the server running?");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>PhishGuard</h1>
      <input
        value={url}
        placeholder="https://example.com"
        onChange={(e) => setUrl(e.target.value)}
      ></input>
      <button onClick={handleScan} disabled={isLoading || url === ""}>
        Scan
      </button>
      {isLoading && <p>Scanning...</p>}
      {result && <p>Verdict: {result.is_phishing ? "Phishing" : "Safe"}</p>}
      {error && <p>{error}</p>}
      <h2>Recent scans</h2>
      <ul>
        {recentScans.map((scan) => (
          <li key={scan.scanned_at}>
            {scan.url} - {scan.is_phishing ? "Phishing" : "Safe"}
          </li>
        ))}
      </ul>
    </main>
  );
}

export default App;
