import React from "react";

export default function Navbar() {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-10">
      <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-emerald-500 flex items-center justify-center font-bold text-slate-950">
            F
          </div>
          <span className="font-semibold text-slate-100">
            FakeNews<span className="text-emerald-400">Detector</span>
          </span>
        </div>

        <nav className="flex items-center gap-4 text-sm text-slate-400">
          <span className="hidden sm:inline-flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            ML service connected
          </span>
          <span className="text-slate-600">v1.0</span>
        </nav>
      </div>
    </header>
  );
}
