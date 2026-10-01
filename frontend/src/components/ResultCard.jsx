import React from "react";

export default function ResultCard({ result }) {
  const { label, confidenceScore, text, probabilities } = result;
  const isReal = label === "REAL";

  const barColor = isReal ? "bg-emerald-500" : "bg-red-500";
  const badgeColor = isReal
    ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/40"
    : "bg-red-500/15 text-red-400 border-red-500/40";

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl shadow-black/20">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Prediction
          </p>
          <span
            className={`mt-1 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-bold ${badgeColor}`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                isReal ? "bg-emerald-400" : "bg-red-400"
              }`}
            />
            {label}
          </span>
        </div>

        <div className="text-right">
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Confidence
          </p>
          <p className="text-2xl font-bold text-slate-100">
            {confidenceScore}%
          </p>
        </div>
      </div>

      <div className="mt-5">
        <div className="flex justify-between text-xs text-slate-500 mb-1">
          <span>Confidence meter</span>
          <span>{confidenceScore}%</span>
        </div>
        <div className="h-3 w-full overflow-hidden rounded-full bg-slate-800">
          <div
            className={`h-full rounded-full ${barColor} transition-all duration-700 ease-out`}
            style={{ width: `${Math.min(confidenceScore, 100)}%` }}
          />
        </div>
      </div>

      {probabilities && (
        <div className="mt-5 grid grid-cols-2 gap-3">
          <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/5 px-3 py-2">
            <p className="text-xs text-emerald-400/80">REAL probability</p>
            <p className="text-lg font-semibold text-emerald-400">
              {probabilities.real}%
            </p>
          </div>
          <div className="rounded-lg border border-red-500/30 bg-red-500/5 px-3 py-2">
            <p className="text-xs text-red-400/80">FAKE probability</p>
            <p className="text-lg font-semibold text-red-400">
              {probabilities.fake}%
            </p>
          </div>
        </div>
      )}

      <div className="mt-5 border-t border-slate-800 pt-4">
        <p className="text-xs uppercase tracking-wide text-slate-500 mb-1">
          Analyzed text
        </p>
        <p className="text-sm text-slate-400 line-clamp-4 whitespace-pre-wrap">
          {text}
        </p>
      </div>
    </div>
  );
}
