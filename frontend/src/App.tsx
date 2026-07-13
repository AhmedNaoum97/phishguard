import { useState } from "react";

  type ScanResult  = {
    verdict: string;
    probability: number;
  }


function App() {
  // 1. State declarations
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<ScanResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  function handleScan () {
    setResult({ verdict: "phishing", probability: 0.97 });
  }

  // 3. What the user sees

  return(
    <main>

      <h1>PhishGuard</h1>
      <input 
      value={url}
      placeholder="https://example.com"
      onChange={(e) => setUrl(e.target.value)}></input>
      <button 
      onClick={handleScan}>Scan</button>
      {result && <p>Verdict: {result.verdict}</p>}
    </main>
  )
}

export default App;