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

  async function loadScans() {
    const response = await fetch("http://127.0.0.1:8000/api/scans");
    const data: ScanResult[] = await response.json();
    setRecentScans(data);
  }

  useEffect(() => {
    loadScans();
  }, []);
  async function handleScan() {
    setIsLoading(true);
    setResult(null);

    const response = await fetch("http://127.0.0.1:8000/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url }),
    });

    const data: ScanResult = await response.json();
    setResult(data);
    await loadScans();
    setIsLoading(false);
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
