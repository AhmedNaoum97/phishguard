import { useState } from "react";

type ScanResult = {
  url: string;
  is_phishing: boolean;
  confidence: number;
  scanned_at: string;
};

function App() {
  // 1. State declarations
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<ScanResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

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
    setIsLoading(false);
  }
  // 3. What the user sees

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
      {result && (
        <p>Verdict: {result.is_phishing ? "Phishing" : "Safe"}</p>
      )}{" "}
    </main>
  );
}

export default App;
