import React, { useState } from "react";
import axios from "axios";

// Points at the Java API Gateway (Spring Boot), which in turn calls the Python ML service.
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

export default function DetectorForm({ onResult, onError, loading, setLoading }) {
  const [text, setText] = useState("");
  const [charError, setCharError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = text.trim();

    if (!trimmed) {
      setCharError("Please paste some article text or a headline first.");
      return;
    }
    if (trimmed.length < 10) {
      setCharError("Please provide at least 10 characters for an accurate scan.");
      return;
    }

    setCharError("");
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/detect`,
        { text: trimmed },
        { timeout: 15000 }
      );
      onResult(response.data);
    } catch (err) {
      if (err.code === "ECONNABORTED") {
        onError("The request timed out. The ML service may be slow to respond.");
      } else if (err.response) {
        const message =
          err.response.data?.error ||
          err.response.data?.message ||
          `Server responded with status ${err.response.status}.`;
        onError(message);
      } else if (err.request) {
        onError(
          "Could not reach the API gateway. Make sure the Java backend is running on port 8080 and the Python ML service is running on port 5000."
        );
      } else {
        onError(err.message || "An unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText("");
    setCharError("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl shadow-black/20"
    >
      <label
        htmlFor="article-text"
        className="block text-sm font-medium text-slate-300 mb-2"
      >
        Article text, headline, or URL
      </label>

      <textarea
        id="article-text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={8}
        placeholder="Paste the news article, headline, or link here..."
        className="w-full resize-y rounded-xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 transition-colors"
        disabled={loading}
      />

      {charError && <p className="mt-2 text-sm text-amber-400">{charError}</p>}

      <div className="mt-4 flex items-center justify-between flex-wrap gap-3">
        <span className="text-xs text-slate-500">
          {text.trim().length} characters
        </span>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleClear}
            disabled={loading}
            className="rounded-lg px-4 py-2 text-sm font-medium text-slate-400 hover:text-slate-200 disabled:opacity-40 transition-colors"
          >
            Clear
          </button>
          <button
            type="submit"
            disabled={loading}
            className="relative overflow-hidden rounded-lg bg-gradient-to-r from-cyan-500 to-emerald-500 px-5 py-2 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition-transform hover:scale-[1.02] disabled:opacity-60 disabled:hover:scale-100"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="h-2 w-2 animate-ping rounded-full bg-slate-950" />
                Scanning...
              </span>
            ) : (
              "Analyze Article"
            )}
          </button>
        </div>
      </div>

      {loading && (
        <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
          <div className="h-full w-1/3 rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 animate-scan" />
        </div>
      )}
    </form>
  );
}
