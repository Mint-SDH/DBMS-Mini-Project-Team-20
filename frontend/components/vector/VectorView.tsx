"use client";

import React, { useState } from "react";
import {
  Binary,
  Search,
  CheckCircle2,
  Sliders,
  RotateCcw,
  Layers,
} from "lucide-react";
import { VectorMatch, API_BASE } from "@/lib/constants";

export function VectorView() {
  const [vectorInputs, setVectorInputs] = useState({
    ipc: 0.62,
    cacheMiss: 36.5,
    branchMispred: 15.2,
    peakMem: 4096,
    duration: 120,
  });
  const [matches, setMatches] = useState<VectorMatch[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    try {
      setSearching(true);
      setError(null);
      const res = await fetch(`${API_BASE}/vector/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ipc_ratio: vectorInputs.ipc,
          cache_miss_rate: vectorInputs.cacheMiss,
          branch_misprediction_rate: vectorInputs.branchMispred,
          peak_memory_mb: vectorInputs.peakMem,
          duration_s: vectorInputs.duration,
          top_k: 5,
        }),
      });
      const data = await res.json();
      setMatches(data.matches || []);
    } catch (err: any) {
      setError(err.message || "Failed to search vector index.");
    } finally {
      setSearching(false);
    }
  };

  const loadPreset = (preset: {
    ipc: number;
    cacheMiss: number;
    branchMispred: number;
    peakMem: number;
    duration: number;
  }) => {
    setVectorInputs(preset);
  };

  return (
    <div className="space-y-4">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#262626]">
        <div>
          <h2 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
            Multidimensional Vector Database & k-NN Anomaly Matcher
          </h2>
          <p className="text-xs text-[#888888] mt-0.5">
            5D Continuous Telemetry Metric Space: <code className="text-[#3ecf8e] font-mono">[IPC, Cache Miss %, Branch Mispred %, Memory, Duration]</code>
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded-md bg-[#1c1c1c] border border-[#2a2a2a] text-[#3ecf8e]">
            Metric Space: <strong>Cosine Similarity (5D Normalized)</strong>
          </span>
        </div>
      </div>

      {/* Vector Sliders Card */}
      <div className="rounded-xl border border-[#262626] bg-[#171717] p-4 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          <div className="p-3 rounded-lg bg-[#141414] border border-[#222222]">
            <div className="flex items-center justify-between text-xs font-mono text-[#888888]">
              <span>IPC Ratio</span>
              <strong className="text-[#3ecf8e]">{vectorInputs.ipc}</strong>
            </div>
            <input
              type="range"
              min="0.1"
              max="4.0"
              step="0.05"
              value={vectorInputs.ipc}
              onChange={(e) =>
                setVectorInputs({ ...vectorInputs, ipc: parseFloat(e.target.value) })
              }
              className="w-full accent-[#3ecf8e] mt-2"
            />
          </div>

          <div className="p-3 rounded-lg bg-[#141414] border border-[#222222]">
            <div className="flex items-center justify-between text-xs font-mono text-[#888888]">
              <span>Cache Miss</span>
              <strong className="text-[#fb923c]">{vectorInputs.cacheMiss}%</strong>
            </div>
            <input
              type="range"
              min="0.0"
              max="60.0"
              step="0.5"
              value={vectorInputs.cacheMiss}
              onChange={(e) =>
                setVectorInputs({ ...vectorInputs, cacheMiss: parseFloat(e.target.value) })
              }
              className="w-full accent-[#3ecf8e] mt-2"
            />
          </div>

          <div className="p-3 rounded-lg bg-[#141414] border border-[#222222]">
            <div className="flex items-center justify-between text-xs font-mono text-[#888888]">
              <span>Branch Mispred</span>
              <strong className="text-[#fbbf24]">{vectorInputs.branchMispred}%</strong>
            </div>
            <input
              type="range"
              min="0.0"
              max="30.0"
              step="0.5"
              value={vectorInputs.branchMispred}
              onChange={(e) =>
                setVectorInputs({
                  ...vectorInputs,
                  branchMispred: parseFloat(e.target.value),
                })
              }
              className="w-full accent-[#3ecf8e] mt-2"
            />
          </div>

          <div className="p-3 rounded-lg bg-[#141414] border border-[#222222]">
            <div className="flex items-center justify-between text-xs font-mono text-[#888888]">
              <span>Peak Memory</span>
              <strong className="text-white">{vectorInputs.peakMem} MB</strong>
            </div>
            <input
              type="number"
              value={vectorInputs.peakMem}
              onChange={(e) =>
                setVectorInputs({ ...vectorInputs, peakMem: parseFloat(e.target.value) })
              }
              className="w-full bg-[#1c1c1c] border border-[#2c2c2c] rounded px-2 py-1 text-xs text-white mt-1.5 font-mono"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handleSearch}
              disabled={searching}
              className="w-full py-2.5 rounded-lg bg-[#3ecf8e] hover:bg-[#34b27b] text-[#121212] font-mono font-bold text-xs flex items-center justify-center gap-2 transition-all disabled:opacity-50 shadow-sm"
            >
              <Search className="w-3.5 h-3.5" />
              <span>{searching ? "Searching..." : "Execute k-NN Match"}</span>
            </button>
          </div>
        </div>

        {/* Benchmark Presets Bar */}
        <div className="pt-3 border-t border-[#222222] flex flex-wrap items-center gap-2 text-xs">
          <span className="text-[#707070] font-mono text-[11px]">Load Golden Archetypes:</span>
          <button
            onClick={() =>
              loadPreset({
                ipc: 0.62,
                cacheMiss: 36.5,
                branchMispred: 15.2,
                peakMem: 4096,
                duration: 120,
              })
            }
            className="px-2.5 py-1 rounded bg-[#1c1c1c] hover:bg-[#252525] text-[#f87171] border border-[#3b1d1d] font-mono text-[11px]"
          >
            Crypto Miner (XMRig)
          </button>
          <button
            onClick={() =>
              loadPreset({
                ipc: 2.85,
                cacheMiss: 3.2,
                branchMispred: 1.2,
                peakMem: 2048,
                duration: 45,
              })
            }
            className="px-2.5 py-1 rounded bg-[#1c1c1c] hover:bg-[#252525] text-[#3ecf8e] border border-[#1d3b2a] font-mono text-[11px]"
          >
            HPC BLAS Matrix
          </button>
          <button
            onClick={() =>
              loadPreset({
                ipc: 0.45,
                cacheMiss: 28.1,
                branchMispred: 14.5,
                peakMem: 256,
                duration: 15,
              })
            }
            className="px-2.5 py-1 rounded bg-[#1c1c1c] hover:bg-[#252525] text-[#fbbf24] border border-[#3b321d] font-mono text-[11px]"
          >
            SYN Flood Port Scan
          </button>
        </div>
      </div>

      {/* Error Output */}
      {error && (
        <div className="p-3 rounded-lg bg-[#251515] border border-[#401f1f] text-[#f87171] text-xs font-mono">
          {error}
        </div>
      )}

      {/* Vector Match Results */}
      {matches.length > 0 && (
        <div className="rounded-xl border border-[#262626] bg-[#171717] p-5 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#262626]">
            <h3 className="text-xs font-semibold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#3ecf8e]" />
              Top-K Nearest Neighbors via Cosine Distance
            </h3>
            <span className="text-[10px] font-mono text-[#707070]">Top 5 Candidates Ranked</span>
          </div>

          <div className="space-y-2">
            {matches.map((item, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg bg-[#141414] border border-[#222222] flex items-center justify-between hover:border-[#333333] transition-all"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-[#1c2c22] text-[#3ecf8e] border border-[#254d37] font-bold">
                      Rank #{idx + 1}
                    </span>
                    <span className="text-xs font-semibold text-white">
                      {item.metadata.name || item.metadata.algo_name || item.vector_id}
                    </span>
                    <span className="text-[10px] font-mono text-[#707070]">
                      ({item.metadata.type})
                    </span>
                  </div>
                  <div className="text-[11px] text-[#707070]">
                    Classification:{" "}
                    <strong className="text-[#f87171] font-semibold">
                      {item.metadata.classification || item.metadata.category}
                    </strong>
                    {item.metadata.hostname && ` • Node: ${item.metadata.hostname}`}
                  </div>
                </div>

                <div className="text-right font-mono">
                  <div className="text-sm font-bold text-[#3ecf8e]">
                    {item.similarity_score}% Sim
                  </div>
                  <div className="text-[10px] text-[#707070]">L2 Distance: {item.distance}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
