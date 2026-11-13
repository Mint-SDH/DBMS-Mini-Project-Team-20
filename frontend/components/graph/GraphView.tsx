"use client";

import React, { useState } from "react";
import {
  Share2,
  Play,
  Network,
  RotateCcw,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";
import { GraphData, API_BASE } from "@/lib/constants";

export function GraphView() {
  const [targetEntity, setTargetEntity] = useState("ALGO_2");
  const [depth, setDepth] = useState(2);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTraverse = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(
        `${API_BASE}/graph/blast-radius?entity_id=${targetEntity}&depth=${depth}`
      );
      const data = await res.json();
      setGraphData(data);
    } catch (err: any) {
      setError(err.message || "Failed to execute Cypher traversal.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#262626]">
        <div>
          <h2 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
            Neo4j Graph Database & Lateral Threat Blast Radius
          </h2>
          <p className="text-xs text-[#888888] mt-0.5">
            Property Graph schema resolving lateral infection traversals without SQL join degeneracy.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded-md bg-[#1c1c1c] border border-[#2a2a2a] text-[#f59e0b]">
            Graph Model: <strong>973 Nodes • 3,300 Edges</strong>
          </span>
        </div>
      </div>

      {/* Traversal Controls Card */}
      <div className="rounded-xl border border-[#262626] bg-[#171717] p-4 flex flex-wrap items-center gap-4">
        <div className="space-y-1">
          <label className="text-[11px] text-[#707070] uppercase font-mono font-semibold">
            Root Entity Node
          </label>
          <select
            value={targetEntity}
            onChange={(e) => setTargetEntity(e.target.value)}
            className="bg-[#121212] border border-[#2a2a2a] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-[#3ecf8e] font-mono"
          >
            <option value="ALGO_2">ALGO_2 (PoW_MemoryHard_Loop)</option>
            <option value="ALGO_6">ALGO_6 (RawSocket_SYN_Scanner)</option>
            <option value="ALGO_4">ALGO_4 (Arbitrage_Tick_Scanner)</option>
            <option value="NODE_28">NODE_28 (node-us-east-23-07)</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-[11px] text-[#707070] uppercase font-mono font-semibold">
            Traversal Depth: <strong className="text-white">{depth} Hops</strong>
          </label>
          <input
            type="range"
            min="1"
            max="3"
            value={depth}
            onChange={(e) => setDepth(parseInt(e.target.value))}
            className="w-36 accent-[#3ecf8e]"
          />
        </div>

        <button
          onClick={handleTraverse}
          disabled={loading}
          className="px-4 py-2 mt-4 rounded-lg bg-[#f59e0b] hover:bg-[#d97706] text-[#121212] font-mono font-bold text-xs flex items-center gap-2 transition-all disabled:opacity-50 shadow-sm"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{loading ? "Traversing..." : "Run Cypher Blast Radius"}</span>
        </button>
      </div>

      {/* Error Output */}
      {error && (
        <div className="p-3 rounded-lg bg-[#251515] border border-[#401f1f] text-[#f87171] text-xs font-mono">
          {error}
        </div>
      )}

      {/* Traversal Results View */}
      {graphData && (
        <div className="rounded-xl border border-[#262626] bg-[#171717] p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#262626]">
            <div>
              <h3 className="text-xs font-semibold text-white uppercase tracking-wider font-mono">
                Compromised Entity Radius: {graphData.root_node?.id}
              </h3>
              <p className="text-[11px] text-[#707070] mt-0.5">
                Total Exposed Lateral Entities: <strong className="text-white">{graphData.total_compromised_nodes}</strong> within {graphData.traversal_depth} hop(s)
              </p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#202020] border border-[#2e2e2e] text-[#888888]">
              Cypher: MATCH (n)-[*1..{depth}]-(m)
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {graphData.nodes?.map((node, idx) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-[#141414] border border-[#222222] space-y-1 hover:border-[#333333] transition-all"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-[#202020] text-[#f59e0b] border border-[#302513] font-bold uppercase">
                    {node.label}
                  </span>
                  <span className="text-[10px] font-mono text-[#707070]">{node.id}</span>
                </div>
                <div className="text-xs font-semibold text-white mt-1">
                  {node.properties?.algo_name ||
                    node.properties?.hostname ||
                    node.properties?.name ||
                    node.properties?.pattern_name ||
                    `Run #${node.properties?.run_id}`}
                </div>
                <div className="text-[10px] text-[#707070] font-mono">
                  {node.properties?.team
                    ? `Team: ${node.properties.team}`
                    : node.properties?.status
                    ? `Status: ${node.properties.status}`
                    : ""}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

