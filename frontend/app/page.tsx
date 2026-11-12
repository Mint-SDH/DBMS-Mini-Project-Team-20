"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  Server,
  Cpu,
  Database,
  Share2,
  Binary,
  Terminal,
  Activity,
  UserCheck,
  AlertTriangle,
  Play,
  RotateCcw,
  CheckCircle2,
  Lock,
  Layers,
  ChevronRight,
  Sliders,
  Search,
  Zap,
  Info
} from "lucide-react";

const API_BASE = "http://localhost:8000/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "threats" | "graph" | "vector" | "sql" | "architecture">("dashboard");
  const [role, setRole] = useState<"sec_admin" | "sec_analyst">("sec_admin");
  const [systemStats, setSystemStats] = useState<any>(null);
  const [criticalThreats, setCriticalThreats] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Vector DB State
  const [vectorInputs, setVectorInputs] = useState({
    ipc: 0.62,
    cacheMiss: 36.5,
    branchMispred: 15.2,
    peakMem: 4096,
    duration: 120
  });
  const [vectorResults, setVectorResults] = useState<any[]>([]);
  const [vectorSearching, setVectorSearching] = useState(false);

  // Graph State
  const [selectedAlgo, setSelectedAlgo] = useState("ALGO_2");
  const [graphDepth, setGraphDepth] = useState(2);
  const [graphData, setGraphData] = useState<any>(null);
  const [graphLoading, setGraphLoading] = useState(false);
  const [quarantineMsg, setQuarantineMsg] = useState<string | null>(null);

  // SQL Query Runner State
  const [selectedPreset, setSelectedPreset] = useState("recursive_cte");
  const [customSQL, setCustomSQL] = useState("");
  const [sqlResult, setSqlResult] = useState<any>(null);
  const [sqlError, setSqlError] = useState<string | null>(null);
  const [sqlExecuting, setSqlExecuting] = useState(false);

  const sqlPresets: Record<string, string> = {
    recursive_cte: `-- Recursive CTE: Polymorphic Algorithm Mutation & Lineage Traversal
WITH RECURSIVE AlgoLineage AS (
    SELECT algo_id, algo_name, version, parent_algo_id, 1 AS lineage_depth, CAST(algo_name AS CHAR(500)) AS lineage_path
    FROM algorithm
    WHERE parent_algo_id IS NULL AND algo_id IN (2, 4, 6, 14)
    UNION ALL
    SELECT a.algo_id, a.algo_name, a.version, a.parent_algo_id, al.lineage_depth + 1, CONCAT(al.lineage_path, ' -> ', a.algo_name)
    FROM algorithm a
    JOIN AlgoLineage al ON a.parent_algo_id = al.algo_id
    WHERE al.lineage_depth < 10
)
SELECT algo_id, lineage_depth, lineage_path FROM AlgoLineage ORDER BY lineage_path LIMIT 15;`,
    correlated_subquery: `-- Correlated Subquery: Runs consuming above-average peak memory for their programming language
SELECT a1.algo_id, a1.algo_name, a1.language, er1.run_id, er1.peak_memory_mb
FROM algorithm a1
JOIN execution_run er1 ON a1.algo_id = er1.algo_id
WHERE er1.peak_memory_mb > (
    SELECT AVG(er2.peak_memory_mb)
    FROM algorithm a2
    JOIN execution_run er2 ON a2.algo_id = er2.algo_id
    WHERE a2.language = a1.language
)
ORDER BY er1.peak_memory_mb DESC
LIMIT 12;`,
    team_cte: `-- Non-Recursive CTE: Team-Level Threat Density & Critical Alert Distribution
WITH TeamThreatMetrics AS (
    SELECT d.team, COUNT(DISTINCT r.run_id) AS total_runs,
           SUM(CASE WHEN dl.alert_level = 'Critical' THEN 1 ELSE 0 END) AS critical_alerts,
           ROUND(AVG(dl.similarity_score), 2) AS mean_similarity
    FROM developer d
    JOIN algorithm a ON d.dev_id = a.dev_id
    JOIN execution_run r ON a.algo_id = r.algo_id
    JOIN fingerprint f ON r.run_id = f.run_id
    JOIN detection_log dl ON f.fingerprint_id = dl.fingerprint_id
    GROUP BY d.team
)
SELECT team, total_runs, critical_alerts, mean_similarity,
       ROUND((critical_alerts / total_runs) * 100, 2) AS threat_density_pct
FROM TeamThreatMetrics
ORDER BY threat_density_pct DESC;`,
    stored_procedure: `CALL GetRunFingerprintProfile(1);`,
    stored_function: `SELECT fingerprint_id, ipc_ratio, CalculateIPCDeviation(fingerprint_id) AS deviation_score_pct
FROM fingerprint
LIMIT 8;`,
    trigger_test: `-- Testing trigger constraint (Will be rejected by trg_validate_fingerprint_bounds)
INSERT INTO fingerprint (run_id, ipc_ratio, cache_miss_rate, branch_misprediction_rate, signature_hash)
VALUES (99999, -1.5, 30.0, 10.0, 'dummyhash12345678901234567890123456789012345678901234567890123456');`
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    setCustomSQL(sqlPresets[selectedPreset]);
  }, [selectedPreset]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, threatsRes] = await Promise.all([
        fetch(`${API_BASE}/dashboard/stats`).then((r) => r.json()),
        fetch(`${API_BASE}/anomalies/critical?limit=15`).then((r) => r.json())
      ]);
      setSystemStats(statsRes);
      setCriticalThreats(threatsRes.data || []);
    } catch (e) {
      console.error("API error", e);
    } finally {
      setLoading(false);
    }
  };

  const handleVectorSearch = async () => {
    setVectorSearching(true);
    try {
      const res = await fetch(`${API_BASE}/vector/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ipc_ratio: vectorInputs.ipc,
          cache_miss_rate: vectorInputs.cacheMiss,
          branch_misprediction_rate: vectorInputs.branchMispred,
          peak_memory_mb: vectorInputs.peakMem,
          duration_s: vectorInputs.duration,
          top_k: 5
        })
      });
      const data = await res.json();
      setVectorResults(data.matches || []);
    } catch (e) {
      console.error(e);
    } finally {
      setVectorSearching(false);
    }
  };

  const handleFetchBlastRadius = async () => {
    setGraphLoading(true);
    try {
      const res = await fetch(`${API_BASE}/graph/blast-radius?entity_id=${selectedAlgo}&depth=${graphDepth}`);
      const data = await res.json();
      setGraphData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setGraphLoading(false);
    }
  };

  const handleQuarantineNode = async (nodeId: number) => {
    if (role !== "sec_admin") {
      alert("Access Denied: Only SecOps Administrator role can quarantine nodes.");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/graph/quarantine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_id: nodeId, reason: "Manual incident response isolation" })
      });
      const data = await res.json();
      setQuarantineMsg(data.message);
      setTimeout(() => setQuarantineMsg(null), 5000);
    } catch (e) {
      console.error(e);
    }
  };

  const handleExecuteSQL = async () => {
    setSqlExecuting(true);
    setSqlError(null);
    setSqlResult(null);
    try {
      const res = await fetch(`${API_BASE}/queries/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: customSQL, role })
      });
      const data = await res.json();
      if (!res.ok) {
        setSqlError(data.detail || "Query execution failed.");
      } else {
        setSqlResult(data);
      }
    } catch (e: any) {
      setSqlError(e.message || "Network error");
    } finally {
      setSqlExecuting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              ExecutionGuard
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-900/60 text-cyan-300 border border-cyan-700/50 font-mono">
                PES DBMS Group 20
              </span>
            </h1>
            <p className="text-xs text-slate-400">Algorithmic Execution Fingerprinting & Threat Profiler</p>
          </div>
        </div>

        {/* Global Role Switcher (RBAC) */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center bg-slate-800/90 rounded-xl p-1 border border-slate-700 text-xs">
            <button
              onClick={() => setRole("sec_admin")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                role === "sec_admin"
                  ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold shadow-md"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              SecOps Admin
            </button>
            <button
              onClick={() => setRole("sec_analyst")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                role === "sec_analyst"
                  ? "bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold shadow-md"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <UserCheck className="w-3.5 h-3.5" />
              Security Analyst
            </button>
          </div>

          <div className="text-right hidden sm:block">
            <span className="text-xs font-mono px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
              DB Role: <strong className="text-cyan-400">{role}</strong>
            </span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Nav */}
        <aside className="w-64 border-r border-slate-800 bg-slate-900/50 p-4 space-y-2 flex flex-col justify-between">
          <nav className="space-y-1 text-sm font-medium">
            {[
              { id: "dashboard", label: "Executive Dashboard", icon: Activity },
              { id: "threats", label: "Threat Detection Log", icon: AlertTriangle },
              { id: "graph", label: "Neo4j Graph Blast Radius", icon: Share2 },
              { id: "vector", label: "Vector DB k-NN Matcher", icon: Binary },
              { id: "sql", label: "SQL & Advanced Queries", icon: Terminal },
              { id: "architecture", label: "System Architecture", icon: Layers }
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition-all ${
                    isActive
                      ? "bg-cyan-600 text-white shadow-lg shadow-cyan-600/30"
                      : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Quick RBAC Banner in Sidebar */}
          <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-2">
            <div className="flex items-center gap-1.5 font-semibold text-slate-300">
              <Lock className="w-3.5 h-3.5 text-cyan-400" />
              <span>RBAC Capabilities</span>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              {role === "sec_admin"
                ? "Full administrative authority: DDL execution, schema mutation, baseline calibration & node quarantine."
                : "Read-only access: Telemetry inspection, vector matching, graph path discovery. DDL/DROP restricted."}
            </p>
          </div>
        </aside>

        {/* Tab Content Area */}
        <main className="flex-1 overflow-y-auto p-6 bg-slate-950 space-y-6">
          {quarantineMsg && (
            <div className="p-4 rounded-xl bg-emerald-950/80 border border-emerald-700/50 text-emerald-300 flex items-center gap-3 animate-fade-in">
              <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
              <span>{quarantineMsg}</span>
            </div>
          )}

          {/* TAB 1: EXECUTIVE DASHBOARD */}
          {activeTab === "dashboard" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Cluster Telemetry Dashboard</h2>
                <p className="text-sm text-slate-400">Microarchitectural execution metrics across heterogeneous cluster nodes.</p>
              </div>

              {/* KPI Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-2xl relative overflow-hidden">
                  <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Total Profiled Runs</div>
                  <div className="text-3xl font-extrabold text-white mt-1">
                    {systemStats ? systemStats.total_runs.toLocaleString() : "4,000"}
                  </div>
                  <div className="text-xs text-emerald-400 mt-2 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>3,637 1:1 Hardware Fingerprints</span>
                  </div>
                </div>

                <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-2xl relative overflow-hidden">
                  <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Critical Rogue Threats</div>
                  <div className="text-3xl font-extrabold text-rose-500 mt-1">
                    {systemStats ? systemStats.critical_threats : "827"}
                  </div>
                  <div className="text-xs text-rose-400 mt-2 flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Auto-Terminated by Trigger</span>
                  </div>
                </div>

                <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-2xl relative overflow-hidden">
                  <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Vector Index Embeddings</div>
                  <div className="text-3xl font-extrabold text-cyan-400 mt-1">
                    {systemStats ? systemStats.vector_db_size : "622"}
                  </div>
                  <div className="text-xs text-cyan-300 mt-2 flex items-center gap-1">
                    <Binary className="w-3.5 h-3.5" />
                    <span>5D Metric Space (Cosine Sim)</span>
                  </div>
                </div>

                <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-2xl relative overflow-hidden">
                  <div className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Neo4j Graph Entities</div>
                  <div className="text-3xl font-extrabold text-amber-400 mt-1">
                    {systemStats ? systemStats.graph_entities : "973"}
                  </div>
                  <div className="text-xs text-amber-300 mt-2 flex items-center gap-1">
                    <Share2 className="w-3.5 h-3.5" />
                    <span>3,310 Traversal Edges</span>
                  </div>
                </div>
              </div>

              {/* Architectural Breakdown & Alert Distribution */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl space-y-4">
                  <h3 className="font-semibold text-slate-200 text-base flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-cyan-400" />
                    Cross-Architecture Hardware Distribution
                  </h3>
                  <div className="space-y-3">
                    {systemStats?.architecture_distribution?.map((item: any, idx: number) => (
                      <div key={idx} className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800/80 flex items-center justify-between">
                        <div>
                          <div className="text-sm font-bold text-white">{item.cpu_architecture}</div>
                          <div className="text-xs text-slate-400">{item.runs.toLocaleString()} execution traces profiled</div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-mono text-cyan-400 font-bold">IPC: {item.avg_ipc}</div>
                          <div className="text-xs text-emerald-400">Normal Bounds</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl space-y-4">
                  <h3 className="font-semibold text-slate-200 text-base flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-rose-400" />
                    Security Alert Severity Classification
                  </h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                    {systemStats?.alert_distribution?.map((alert: any, idx: number) => {
                      const colors: Record<string, string> = {
                        Critical: "bg-rose-950/50 border-rose-800 text-rose-300",
                        High: "bg-orange-950/50 border-orange-800 text-orange-300",
                        Medium: "bg-amber-950/50 border-amber-800 text-amber-300",
                        Low: "bg-blue-950/50 border-blue-800 text-blue-300",
                        Info: "bg-slate-900 border-slate-700 text-slate-300"
                      };
                      return (
                        <div key={idx} className={`p-3 rounded-xl border ${colors[alert.alert_level] || colors.Info}`}>
                          <div className="text-xs font-semibold">{alert.alert_level}</div>
                          <div className="text-xl font-extrabold mt-1">{alert.count.toLocaleString()}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: THREAT DETECTION LOG */}
          {activeTab === "threats" && (
            <div className="space-y-6">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                    <AlertTriangle className="w-6 h-6 text-rose-500" />
                    Critical & High Severity Anomalies
                  </h2>
                  <p className="text-sm text-slate-400">Live view backed by relational SQL view: <code className="text-cyan-400">vw_critical_security_anomalies</code></p>
                </div>
              </div>

              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 font-mono">
                      <tr>
                        <th className="py-3 px-4">Run ID</th>
                        <th className="py-3 px-4">Algorithm</th>
                        <th className="py-3 px-4">Developer</th>
                        <th className="py-3 px-4">Node Hostname</th>
                        <th className="py-3 px-4">Detected Signature</th>
                        <th className="py-3 px-4">Similarity</th>
                        <th className="py-3 px-4">Classification</th>
                        <th className="py-3 px-4">Mitigation Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {criticalThreats.map((row: any, idx: number) => (
                        <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                          <td className="py-3 px-4 font-mono font-bold text-cyan-400">#{row.run_id}</td>
                          <td className="py-3 px-4 font-medium text-white">{row.algo_name}</td>
                          <td className="py-3 px-4 text-slate-300">{row.developer_name} ({row.team})</td>
                          <td className="py-3 px-4 font-mono text-slate-400">{row.hostname}</td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 font-mono">
                              {row.detected_threat_signature}
                            </span>
                          </td>
                          <td className="py-3 px-4 font-bold text-rose-400 font-mono">{row.similarity_score}%</td>
                          <td className="py-3 px-4 text-slate-200">{row.classification_result}</td>
                          <td className="py-3 px-4">
                            <button
                              onClick={() => handleQuarantineNode(1)}
                              className="px-2.5 py-1 rounded bg-rose-600/80 hover:bg-rose-600 text-white font-semibold text-[11px] transition-all flex items-center gap-1"
                            >
                              <ShieldAlert className="w-3 h-3" />
                              Quarantine
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: NEO4J GRAPH BLAST RADIUS */}
          {activeTab === "graph" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                  <Share2 className="w-6 h-6 text-amber-400" />
                  Neo4j Threat Graph & Lateral Blast Radius
                </h2>
                <p className="text-sm text-slate-400">Multi-hop graph traversal to evaluate lateral malware propagation and cluster exposure.</p>
              </div>

              {/* Traversal Query Controls */}
              <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl flex flex-wrap items-center gap-4">
                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Target Root Node</label>
                  <select
                    value={selectedAlgo}
                    onChange={(e) => setSelectedAlgo(e.target.value)}
                    className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white"
                  >
                    <option value="ALGO_2">ALGO_2 (PoW_MemoryHard_Loop)</option>
                    <option value="ALGO_6">ALGO_6 (RawSocket_SYN_Scanner)</option>
                    <option value="ALGO_4">ALGO_4 (Arbitrage_Tick_Scanner)</option>
                    <option value="NODE_28">NODE_28 (node-us-east-23-07)</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-slate-400">Traversal Depth (Hops: {graphDepth})</label>
                  <input
                    type="range"
                    min="1"
                    max="3"
                    value={graphDepth}
                    onChange={(e) => setGraphDepth(parseInt(e.target.value))}
                    className="w-32 accent-cyan-500"
                  />
                </div>

                <button
                  onClick={handleFetchBlastRadius}
                  disabled={graphLoading}
                  className="px-4 py-2 mt-4 rounded-xl bg-amber-500 hover:bg-amber-600 text-black font-bold text-xs flex items-center gap-2 transition-all"
                >
                  <Play className="w-3.5 h-3.5" />
                  {graphLoading ? "Traversing..." : "Run Cypher Blast Radius"}
                </button>
              </div>

              {/* Graph Results View */}
              {graphData && (
                <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                      <h4 className="font-bold text-white text-base">Traversal Report: {graphData.root_node?.id}</h4>
                      <p className="text-xs text-slate-400">
                        Total Reachable Entities: <strong className="text-amber-400">{graphData.total_compromised_nodes}</strong> within {graphData.traversal_depth} hops
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {graphData.nodes?.map((n: any, idx: number) => (
                      <div key={idx} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                            {n.label}
                          </span>
                          <span className="text-xs font-mono text-slate-400">{n.id}</span>
                        </div>
                        <div className="text-sm font-semibold text-white mt-1">
                          {n.properties?.algo_name || n.properties?.hostname || n.properties?.name || n.properties?.pattern_name || `Run #${n.properties?.run_id}`}
                        </div>
                        <div className="text-xs text-slate-400">
                          {n.properties?.team ? `Team: ${n.properties.team}` : n.properties?.status ? `Status: ${n.properties.status}` : ""}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: VECTOR DATABASE K-NN MATCHER */}
          {activeTab === "vector" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                  <Binary className="w-6 h-6 text-cyan-400" />
                  Multidimensional Vector DB & k-NN Anomaly Matcher
                </h2>
                <p className="text-sm text-slate-400">
                  Calculates Cosine Similarity across 5D continuous telemetry space: <code className="text-cyan-400">[IPC, Cache Miss %, Branch Mispred %, Memory, Duration]</code>.
                </p>
              </div>

              {/* Slider Inputs */}
              <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                  <div>
                    <label className="text-xs text-slate-400 font-mono">IPC Ratio ({vectorInputs.ipc})</label>
                    <input
                      type="range"
                      min="0.1"
                      max="4.0"
                      step="0.05"
                      value={vectorInputs.ipc}
                      onChange={(e) => setVectorInputs({ ...vectorInputs, ipc: parseFloat(e.target.value) })}
                      className="w-full accent-cyan-500 mt-2"
                    />
                  </div>

                  <div>
                    <label className="text-xs text-slate-400 font-mono">Cache Miss Rate ({vectorInputs.cacheMiss}%)</label>
                    <input
                      type="range"
                      min="0.0"
                      max="60.0"
                      step="0.5"
                      value={vectorInputs.cacheMiss}
                      onChange={(e) => setVectorInputs({ ...vectorInputs, cacheMiss: parseFloat(e.target.value) })}
                      className="w-full accent-cyan-500 mt-2"
                    />
                  </div>

                  <div>
                    <label className="text-xs text-slate-400 font-mono">Branch Mispred ({vectorInputs.branchMispred}%)</label>
                    <input
                      type="range"
                      min="0.0"
                      max="30.0"
                      step="0.5"
                      value={vectorInputs.branchMispred}
                      onChange={(e) => setVectorInputs({ ...vectorInputs, branchMispred: parseFloat(e.target.value) })}
                      className="w-full accent-cyan-500 mt-2"
                    />
                  </div>

                  <div>
                    <label className="text-xs text-slate-400 font-mono">Peak Memory (MB)</label>
                    <input
                      type="number"
                      value={vectorInputs.peakMem}
                      onChange={(e) => setVectorInputs({ ...vectorInputs, peakMem: parseFloat(e.target.value) })}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1 text-xs text-white mt-1"
                    />
                  </div>

                  <div className="flex items-end">
                    <button
                      onClick={handleVectorSearch}
                      disabled={vectorSearching}
                      className="w-full py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-black font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-500/20"
                    >
                      <Search className="w-3.5 h-3.5" />
                      {vectorSearching ? "Searching..." : "k-NN Match (Top 5)"}
                    </button>
                  </div>
                </div>

                {/* Presets */}
                <div className="pt-2 border-t border-slate-800 flex items-center gap-2 text-xs">
                  <span className="text-slate-400">Load Benchmark Preset:</span>
                  <button
                    onClick={() => setVectorInputs({ ipc: 0.62, cacheMiss: 36.5, branchMispred: 15.2, peakMem: 4096, duration: 120 })}
                    className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-rose-300 border border-rose-900/60"
                  >
                    Cryptojacking Malware (XMRig)
                  </button>
                  <button
                    onClick={() => setVectorInputs({ ipc: 2.85, cacheMiss: 3.2, branchMispred: 1.2, peakMem: 2048, duration: 45 })}
                    className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-emerald-900/60"
                  >
                    HPC BLAS Matrix Multiply
                  </button>
                  <button
                    onClick={() => setVectorInputs({ ipc: 0.45, cacheMiss: 28.1, branchMispred: 14.5, peakMem: 256, duration: 15 })}
                    className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-amber-300 border border-amber-900/60"
                  >
                    Port Scan SYN Probe
                  </button>
                </div>
              </div>

              {/* Vector k-NN Match Results */}
              {vectorResults.length > 0 && (
                <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl space-y-3">
                  <h3 className="font-semibold text-white text-base flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    Top-K Nearest Neighbor Matches in Vector Space
                  </h3>
                  <div className="space-y-2.5">
                    {vectorResults.map((item, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold">
                              Rank #{idx + 1}
                            </span>
                            <span className="text-sm font-bold text-white">
                              {item.metadata.name || item.metadata.algo_name || item.vector_id}
                            </span>
                            <span className="text-xs text-slate-400">({item.metadata.type})</span>
                          </div>
                          <div className="text-xs text-slate-400">
                            Classification: <strong className="text-rose-400">{item.metadata.classification || item.metadata.category}</strong>
                            {item.metadata.hostname && ` • Host: ${item.metadata.hostname}`}
                          </div>
                        </div>

                        <div className="text-right">
                          <div className="text-lg font-mono font-extrabold text-cyan-400">
                            {item.similarity_score}% Sim
                          </div>
                          <div className="text-[11px] font-mono text-slate-500">L2 Dist: {item.distance}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 5: SQL PLAYGROUND & ADVANCED QUERIES */}
          {activeTab === "sql" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                  <Terminal className="w-6 h-6 text-cyan-400" />
                  Interactive SQL & Advanced Query Engine
                </h2>
                <p className="text-sm text-slate-400">
                  Execute Recursive CTEs, Correlated Subqueries, Stored Procedures, and Triggers with dynamic RBAC gating.
                </p>
              </div>

              {/* Preset Selector */}
              <div className="flex flex-wrap gap-2">
                {[
                  { id: "recursive_cte", label: "Recursive CTE: Algo Lineages" },
                  { id: "correlated_subquery", label: "Correlated Subquery: Peak Memory" },
                  { id: "team_cte", label: "CTE: Team Threat Ranking" },
                  { id: "stored_procedure", label: "Procedure: GetRunFingerprintProfile" },
                  { id: "stored_function", label: "Function: CalculateIPCDeviation" },
                  { id: "trigger_test", label: "Trigger: Bounds Violation Test" }
                ].map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setSelectedPreset(p.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      selectedPreset === p.id
                        ? "bg-cyan-600 text-white font-bold"
                        : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>

              {/* Query Editor */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden p-4 space-y-3">
                <textarea
                  value={customSQL}
                  onChange={(e) => setCustomSQL(e.target.value)}
                  rows={8}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 font-mono text-xs text-cyan-300 focus:outline-none focus:border-cyan-500"
                />

                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">
                    Executing under user context: <strong className="text-cyan-400">{role === "sec_admin" ? "admin_user (sec_admin)" : "analyst_user (sec_analyst)"}</strong>
                  </span>
                  <button
                    onClick={handleExecuteSQL}
                    disabled={sqlExecuting}
                    className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold text-xs flex items-center gap-2 hover:opacity-90 transition-all shadow-lg shadow-cyan-500/20"
                  >
                    <Play className="w-3.5 h-3.5" />
                    {sqlExecuting ? "Executing..." : "Execute Query"}
                  </button>
                </div>
              </div>

              {/* Query Error / Result Output */}
              {sqlError && (
                <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-800 text-rose-300 text-xs font-mono space-y-1">
                  <div className="font-bold flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                    Query Execution Error:
                  </div>
                  <div>{sqlError}</div>
                </div>
              )}

              {sqlResult && (
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden p-4 space-y-3">
                  <div className="text-xs text-slate-400 font-mono">
                    Returned <strong>{sqlResult.count || sqlResult.affected_rows || 0}</strong> record(s)
                  </div>
                  {sqlResult.rows && sqlResult.rows.length > 0 ? (
                    <div className="overflow-x-auto max-h-96">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 font-mono">
                          <tr>
                            {Object.keys(sqlResult.rows[0]).map((k, i) => (
                              <th key={i} className="py-2.5 px-3">{k}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60 font-mono">
                          {sqlResult.rows.map((r: any, idx: number) => (
                            <tr key={idx} className="hover:bg-slate-800/40">
                              {Object.values(r).map((v: any, j: number) => (
                                <td key={j} className="py-2 px-3 text-slate-300">{String(v)}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-xs text-emerald-400 font-mono">
                      {sqlResult.message || "Statement executed successfully."}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 6: SYSTEM ARCHITECTURE & JUSTIFICATION */}
          {activeTab === "architecture" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                  <Layers className="w-6 h-6 text-cyan-400" />
                  Tripartite Database Architecture & Technology Justification
                </h2>
                <p className="text-sm text-slate-400">
                  Comprehensive architectural rationale for pairing Relational, Graph, and Vector database engines.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900/70 border border-slate-800 p-5 rounded-2xl space-y-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-950 border border-blue-800 flex items-center justify-center text-blue-400">
                    <Database className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-white text-base">1. MySQL 8.0 Relational Core</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Provides ACID guarantees, strong relational foreign key constraints, 1:1 run-to-fingerprint cardinality, and real-time triggers for automated rogue process termination.
                  </p>
                  <ul className="text-xs text-slate-300 space-y-1 font-mono">
                    <li>• 7 Strongly Typed Entities</li>
                    <li>• Recursive CTEs (Lineages)</li>
                    <li>• Native RBAC Roles</li>
                  </ul>
                </div>

                <div className="bg-slate-900/70 border border-slate-800 p-5 rounded-2xl space-y-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-950 border border-amber-800 flex items-center justify-center text-amber-400">
                    <Share2 className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-white text-base">2. Neo4j Graph Database</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Overcomes relational join degeneracy when analyzing multi-hop connections. Computes 3-hop threat blast radii to pinpoint compromised compute nodes and lateral infection pathways.
                  </p>
                  <ul className="text-xs text-slate-300 space-y-1 font-mono">
                    <li>• Index-Free Adjacency</li>
                    <li>• Cypher Traversal Paths</li>
                    <li>• One-Click Node Quarantine</li>
                  </ul>
                </div>

                <div className="bg-slate-900/70 border border-slate-800 p-5 rounded-2xl space-y-3">
                  <div className="w-10 h-10 rounded-xl bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400">
                    <Binary className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-white text-base">3. 5D Vector Database</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Maps continuous microprocessor counters into normalized vector coordinates. Employs Cosine Distance k-NN retrieval for sub-millisecond zero-day polymorphic malware detection.
                  </p>
                  <ul className="text-xs text-slate-300 space-y-1 font-mono">
                    <li>• 5D Normalized Space</li>
                    <li>• Cosine Sim &gt; 97%</li>
                    <li>• Vector RUD Lifecycle</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
