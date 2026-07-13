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

  function handleScan() {
    setResult({
      url: "https://example.com",
      is_phishing: true,
      confidence: 0.97,
      scanned_at: "2026-07-13",
    });
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
      <button onClick={handleScan}>Scan</button>
      {result && <p>Verdict: {result.is_phishing ? "Phishing" : "Safe"}</p>}
    </main>
  );
}

export default App;
