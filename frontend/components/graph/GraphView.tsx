"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Share2,
  Play,
  RotateCcw,
  CheckCircle2,
  ShieldAlert,
  Info,
  Maximize2,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { GraphData, GraphNode, GraphEdge, API_BASE } from "@/lib/constants";

// Node styling by Neo4j entity label
const NODE_STYLES: Record<string, { bg: string; border: string; text: string; ring: string }> = {
  Algorithm: {
    bg: "#1e1b4b",
    border: "#4338ca",
    text: "#a5b4fc",
    ring: "#6366f1",
  },
  ExecutionRun: {
    bg: "#311010",
    border: "#7f1d1d",
    text: "#fca5a5",
    ring: "#ef4444",
  },
  Developer: {
    bg: "#06281e",
    border: "#065f46",
    text: "#6ee7b7",
    ring: "#10b981",
  },
  ComputeNode: {
    bg: "#1e293b",
    border: "#334155",
    text: "#cbd5e1",
    ring: "#64748b",
  },
  BaselinePattern: {
    bg: "#2e1065",
    border: "#581c87",
    text: "#d8b4fe",
    ring: "#a855f7",
  },
};

export function GraphView() {
  const [targetEntity, setTargetEntity] = useState("ALGO_2");
  const [depth, setDepth] = useState(2);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const handleTraverse = async (entity = targetEntity, traversalDepth = depth) => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(
        `${API_BASE}/graph/blast-radius?entity_id=${entity}&depth=${traversalDepth}`
      );
      if (!res.ok) throw new Error("Graph traversal API returned an error.");
      const data = await res.json();
      setGraphData(data);
      if (data.root_node) {
        setSelectedNode(data.root_node);
      }
    } catch (err: any) {
      setError(err.message || "Failed to execute Cypher traversal.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleTraverse("ALGO_2", 2);
  }, []);

  // Compute 2D coordinates for visual network graph
  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];
  const rootId = graphData?.root_node?.id || targetEntity;

  // Layout nodes around center root node
  const width = 800;
  const height = 480;
  const centerX = width / 2;
  const centerY = height / 2;

  const nodePositions: Record<string, { x: number; y: number }> = {};
  
  if (nodes.length > 0) {
    // Root in center
    nodePositions[rootId] = { x: centerX, y: centerY };

    // Group remaining nodes by label for neat concentric layout
    const otherNodes = nodes.filter((n) => n.id !== rootId);
    const radiusStep = otherNodes.length > 8 ? 160 : 180;

    otherNodes.forEach((node, idx) => {
      const angle = (idx / otherNodes.length) * 2 * Math.PI - Math.PI / 2;
      // Slight radius jitter to prevent overlapping
      const r = radiusStep + (idx % 2 === 0 ? 30 : -20);
      nodePositions[node.id] = {
        x: Math.max(70, Math.min(width - 70, centerX + r * Math.cos(angle))),
        y: Math.max(60, Math.min(height - 60, centerY + r * Math.sin(angle))),
      };
    });
  }

  return (
    <div className="space-y-4">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#262626]">
        <div>
          <h2 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
            Neo4j Property Graph & Lateral Threat Blast Radius
          </h2>
          <p className="text-xs text-[#888888] mt-0.5">
            Real-time multi-hop Cypher traversal resolving lateral infection spread across cluster nodes.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded-md bg-[#1c1c1c] border border-[#2a2a2a] text-[#f59e0b]">
            Graph Model: <strong>973 Nodes • 3,300 Edges</strong>
          </span>
        </div>
      </div>

      {/* Traversal Controls Bar */}
      <div className="rounded-xl border border-[#262626] bg-[#171717] p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="space-y-1">
            <label className="text-[11px] text-[#707070] uppercase font-mono font-semibold">
              Root Entity Node
            </label>
            <select
              value={targetEntity}
              onChange={(e) => {
                setTargetEntity(e.target.value);
                handleTraverse(e.target.value, depth);
              }}
              className="bg-[#121212] border border-[#2a2a2a] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-[#3ecf8e] font-mono"
            >
              <option value="ALGO_2">ALGO_2 (PoW_MemoryHard_Loop)</option>
              <option value="ALGO_6">ALGO_6 (RawSocket_SYN_Scanner)</option>
              <option value="ALGO_4">ALGO_4 (Arbitrage_Tick_Scanner)</option>
              <option value="NODE_28">NODE_28 (node-us-east-23-07)</option>
              <option value="DEV_74">DEV_74 (Joseph Brennan)</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-[11px] text-[#707070] uppercase font-mono font-semibold">
              Cypher Depth: <strong className="text-white">{depth} Hop(s)</strong>
            </label>
            <input
              type="range"
              min="1"
              max="3"
              value={depth}
              onChange={(e) => {
                const newD = parseInt(e.target.value);
                setDepth(newD);
                handleTraverse(targetEntity, newD);
              }}
              className="w-32 accent-[#3ecf8e]"
            />
          </div>
        </div>

        <button
          onClick={() => handleTraverse(targetEntity, depth)}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-[#f59e0b] hover:bg-[#d97706] text-[#121212] font-mono font-bold text-xs flex items-center gap-2 transition-all disabled:opacity-50 shadow-sm"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{loading ? "Traversing Graph..." : "Execute Cypher Traversal"}</span>
        </button>
      </div>

      {/* Main Interactive Visual Canvas & Inspector Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Left 3 Cols: SVG Interactive Graph Canvas */}
        <div className="lg:col-span-3 rounded-xl border border-[#262626] bg-[#141414] overflow-hidden shadow-sm relative flex flex-col items-center justify-center p-2 min-h-[500px]">
          {/* Legend Overlay */}
          <div className="absolute top-3 left-3 z-10 flex flex-wrap gap-2 text-[10px] font-mono bg-[#171717]/80 backdrop-blur-sm p-2 rounded-lg border border-[#262626]">
            {Object.entries(NODE_STYLES).map(([label, style]) => (
              <div key={label} className="flex items-center gap-1.5">
                <span
                  className="w-2.5 h-2.5 rounded-full border"
                  style={{ backgroundColor: style.bg, borderColor: style.border }}
                />
                <span className="text-[#a0a0a0]">{label}</span>
              </div>
            ))}
          </div>

          {/* Cypher Breadcrumb */}
          <div className="absolute top-3 right-3 z-10 text-[10px] font-mono px-2 py-1 rounded bg-[#171717]/90 border border-[#262626] text-[#f59e0b]">
            <code>MATCH (root:{graphData?.root_node?.label} &#123;id: &quot;{rootId}&quot;&#125;)-[*1..{depth}]-(m) RETURN *;</code>
          </div>

          {/* SVG Graph Canvas */}
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="w-full h-[460px] select-none"
          >
            <defs>
              <marker
                id="arrow"
                viewBox="0 0 10 10"
                refX="28"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#444444" />
              </marker>
            </defs>

            {/* Edges */}
            {edges.map((edge, idx) => {
              const src = nodePositions[edge.source];
              const tgt = nodePositions[edge.target];
              if (!src || !tgt) return null;

              const midX = (src.x + tgt.x) / 2;
              const midY = (src.y + tgt.y) / 2;

              return (
                <g key={`edge-${idx}`} className="group">
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke="#2e2e2e"
                    strokeWidth="1.5"
                    strokeDasharray={edge.type === "DERIVED_FROM" ? "4,4" : undefined}
                    markerEnd="url(#arrow)"
                    className="group-hover:stroke-[#f59e0b] transition-all"
                  />
                  {/* Edge Type Label */}
                  <text
                    x={midX}
                    y={midY - 4}
                    fill="#666666"
                    fontSize="8"
                    fontFamily="monospace"
                    textAnchor="middle"
                    className="group-hover:fill-white pointer-events-none"
                  >
                    {edge.type}
                  </text>
                </g>
              );
            })}

            {/* Nodes */}
            {nodes.map((node) => {
              const pos = nodePositions[node.id];
              if (!pos) return null;

              const isRoot = node.id === rootId;
              const isSelected = selectedNode?.id === node.id;
              const style = NODE_STYLES[node.label] || NODE_STYLES.Algorithm;

              return (
                <g
                  key={node.id}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  onClick={() => setSelectedNode(node)}
                  className="cursor-pointer transition-transform hover:scale-110"
                >
                  {/* Halo Ring on Selection / Root */}
                  {(isSelected || isRoot) && (
                    <circle
                      r={isRoot ? 32 : 26}
                      fill="none"
                      stroke={style.ring}
                      strokeWidth="2"
                      strokeDasharray="3,3"
                      className="animate-spin"
                      style={{ animationDuration: "12s" }}
                    />
                  )}

                  {/* Core Node Circle */}
                  <circle
                    r={isRoot ? 24 : 19}
                    fill={style.bg}
                    stroke={isSelected ? "#ffffff" : style.border}
                    strokeWidth={isSelected ? 2 : 1.5}
                    className="shadow-md"
                  />

                  {/* Node Label / ID Text */}
                  <text
                    textAnchor="middle"
                    dy="4"
                    fill={style.text}
                    fontSize={isRoot ? "10" : "8"}
                    fontFamily="monospace"
                    fontWeight="bold"
                    className="pointer-events-none"
                  >
                    {node.id}
                  </text>

                  {/* Subtitle Name below node */}
                  <text
                    textAnchor="middle"
                    dy={isRoot ? "36" : "30"}
                    fill="#cccccc"
                    fontSize="9"
                    fontFamily="sans-serif"
                    className="pointer-events-none drop-shadow-sm font-medium"
                  >
                    {node.properties?.algo_name
                      ? node.properties.algo_name.slice(0, 14)
                      : node.properties?.hostname
                      ? node.properties.hostname.slice(0, 14)
                      : node.properties?.name || node.label}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Quick Helper Footer */}
          <div className="w-full text-center py-1 text-[11px] font-mono text-[#707070] border-t border-[#1e1e1e]">
            Click any node in the blast radius to inspect its property graph attributes.
          </div>
        </div>

        {/* Right 1 Col: Entity Inspector Sidebar */}
        <div className="rounded-xl border border-[#262626] bg-[#171717] p-4 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#262626]">
              <h3 className="text-xs font-semibold text-white tracking-wider font-mono uppercase">
                Graph Inspector
              </h3>
              {selectedNode && (
                <span
                  className="text-[9px] font-mono px-2 py-0.5 rounded uppercase font-bold"
                  style={{
                    backgroundColor: NODE_STYLES[selectedNode.label]?.bg || "#202020",
                    color: NODE_STYLES[selectedNode.label]?.text || "#ffffff",
                    border: `1px solid ${NODE_STYLES[selectedNode.label]?.border || "#333"}`,
                  }}
                >
                  {selectedNode.label}
                </span>
              )}
            </div>

            {selectedNode ? (
              <div className="space-y-3">
                <div>
                  <div className="text-[10px] text-[#707070] font-mono uppercase font-semibold">
                    Node ID
                  </div>
                  <div className="text-sm font-bold text-white font-mono mt-0.5">
                    {selectedNode.id}
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-[#222222]">
                  <div className="text-[10px] text-[#707070] font-mono uppercase font-semibold">
                    Cypher Properties (JSON)
                  </div>
                  <div className="bg-[#121212] p-2.5 rounded-lg border border-[#262626] font-mono text-xs space-y-1.5 text-[#ededed]">
                    {Object.entries(selectedNode.properties || {}).map(([key, val]) => (
                      <div key={key} className="flex justify-between items-start gap-2">
                        <span className="text-[#888888]">{key}:</span>
                        <span className="text-[#3ecf8e] text-right font-semibold break-all">
                          {String(val)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Threat Mitigation helper */}
                {selectedNode.label === "ComputeNode" && (
                  <div className="p-3 rounded-lg bg-[#241313] border border-[#3e1f1f] space-y-2 mt-3">
                    <div className="flex items-center gap-1.5 text-xs text-[#f87171] font-bold">
                      <ShieldAlert className="w-3.5 h-3.5" />
                      <span>Lateral Host Exposure</span>
                    </div>
                    <p className="text-[11px] text-[#fca5a5]">
                      Server <code className="text-white font-mono">{selectedNode.properties?.hostname}</code> is within the multi-hop infection radius.
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="py-12 text-center text-[#707070] font-mono text-xs">
                Select a graph node to inspect its properties.
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-[#222222] text-[11px] font-mono text-[#707070]">
            <div>Traversed Entities: <strong className="text-white">{nodes.length}</strong></div>
            <div>Multi-Hop Edges: <strong className="text-white">{edges.length}</strong></div>
          </div>
        </div>
      </div>
    </div>
  );
}

