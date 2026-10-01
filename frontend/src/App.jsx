import React, { useState } from "react";
import Navbar from "./components/Navbar.jsx";
import DetectorForm from "./components/DetectorForm.jsx";
import ResultCard from "./components/ResultCard.jsx";

export default function App() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const handleNewResult = (data) => {
    setResult(data);
    setError(null);
    setHistory((prev) => [{ ...data, id: Date.now() }, ...prev].slice(0, 5));
  };

  const handleError = (message) => {
    setError(message);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      <Navbar />

      <main className="max-w-3xl mx-auto px-4 py-10">
        <div className="text-center mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-transparent">
            Fake News Detector
          </h1>
          <p className="mt-3 text-slate-400 max-w-xl mx-auto">
            Paste an article, headline, or link below. Our AI pipeline scans
            the text and estimates whether it looks REAL or FAKE.
          </p>
        </div>

        <DetectorForm
          onResult={handleNewResult}
          onError={handleError}
          loading={loading}
          setLoading={setLoading}
        />

        {error && (
          <div className="mt-6 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-red-300">
            <p className="font-semibold">Connection error</p>
            <p className="text-sm text-red-300/80">{error}</p>
          </div>
        )}

        {result && !error && (
          <div className="mt-6">
            <ResultCard result={result} />
          </div>
        )}

        {history.length > 0 && (
          <div className="mt-12">
            <h2 className="text-lg font-semibold text-slate-300 mb-3">
              Recent scans
            </h2>
            <ul className="space-y-2">
              {history.map((item) => (
                <li
                  key={item.id}
                  className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 px-4 py-2 text-sm gap-4"
                >
                  <span className="truncate max-w-[60%] text-slate-400">
                    {item.text}
                  </span>
                  <span
                    className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-semibold ${
                      item.label === "REAL"
                        ? "bg-emerald-500/20 text-emerald-400"
                        : "bg-red-500/20 text-red-400"
                    }`}
                  >
                    {item.label} · {item.confidenceScore}%
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <footer className="mt-16 text-center text-xs text-slate-600">
          Built with React, Spring Boot, and FastAPI. For educational
          purposes only, not a substitute for professional fact-checking.
        </footer>
      </main>
    </div>
  );
}
