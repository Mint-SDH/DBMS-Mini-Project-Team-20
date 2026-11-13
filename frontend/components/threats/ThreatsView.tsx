"use client";

import React, { useState, useEffect } from "react";
import {
  AlertTriangle,
  ShieldAlert,
  Search,
  Filter,
  CheckCircle2,
  Lock,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { AnomalyRecord, RoleType, API_BASE } from "@/lib/constants";

interface ThreatsViewProps {
  threats: AnomalyRecord[];
  role: RoleType;
  onQuarantineNode: (nodeId: number, hostname: string) => void;
  quarantinedNodes: Set<number>;
  totalCritical?: number;
  totalHigh?: number;
}

export function ThreatsView({
  threats: initialThreats,
  role,
  onQuarantineNode,
  quarantinedNodes,
  totalCritical,
  totalHigh,
}: ThreatsViewProps) {
  const [filterQuery, setFilterQuery] = useState("");
  const [selectedSeverity, setSelectedSeverity] = useState<string>("ALL");
  const [page, setPage] = useState(1);
  const pageSize = 15;
  const [data, setData] = useState<AnomalyRecord[]>(initialThreats);
  const [totalRecords, setTotalRecords] = useState<number>(9078);
  const [loading, setLoading] = useState(false);

  // Fetch paginated records directly from the database whenever filter or page changes
  useEffect(() => {
    let isMounted = true;
    const fetchPageData = async () => {
      setLoading(true);
      try {
        const offset = (page - 1) * pageSize;
        const res = await fetch(
          `${API_BASE}/anomalies/critical?limit=${pageSize}&offset=${offset}&severity=${selectedSeverity}`
        );
        if (res.ok) {
          const json = await res.json();
          if (isMounted) {
            setData(json.data || []);
            setTotalRecords(json.total || 0);
          }
        }
      } catch (err) {
        console.error("Error fetching paginated threat logs:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchPageData();
    return () => {
      isMounted = false;
    };
  }, [page, selectedSeverity]);

  // Client-side quick filter on current loaded page for instant search typing
  const displayThreats = data.filter((item) => {
    if (!filterQuery) return true;
    return (
      item.algo_name.toLowerCase().includes(filterQuery.toLowerCase()) ||
      item.hostname.toLowerCase().includes(filterQuery.toLowerCase()) ||
      item.developer_name.toLowerCase().includes(filterQuery.toLowerCase()) ||
      item.detected_threat_signature.toLowerCase().includes(filterQuery.toLowerCase())
    );
  });

  const totalPages = Math.ceil(totalRecords / pageSize) || 1;

  return (
    <div className="space-y-4">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#262626]">
        <div>
          <h2 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
            Threat Audit Log
          </h2>
          <p className="text-xs text-[#888888] mt-0.5">
            Relational Security View: <code className="text-[#3ecf8e] font-mono">vw_critical_security_anomalies</code>
            <span className="text-[#a0a0a0]"> ({totalRecords.toLocaleString()} matching records in MySQL)</span>
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-2 text-xs">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-[#707070] absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter by host, algo or developer..."
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              className="bg-[#171717] border border-[#2a2a2a] rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-[#606060] focus:outline-none focus:border-[#3ecf8e] w-56 font-mono"
            />
          </div>

          <select
            value={selectedSeverity}
            onChange={(e) => {
              setSelectedSeverity(e.target.value);
              setPage(1); // Reset to page 1 on filter change
            }}
            className="bg-[#171717] border border-[#2a2a2a] rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-[#3ecf8e] font-mono"
          >
            <option value="ALL">All Severities (9,078 Total)</option>
            <option value="Critical">Critical (827 Auto-Terminated)</option>
            <option value="High">High (889 Threats)</option>
            <option value="Medium">Medium (2,826 Drift)</option>
            <option value="Low">Low (1,860 Minor)</option>
            <option value="Info">Info (2,676 Verified Safe)</option>
          </select>
        </div>
      </div>

      {/* Relational Table */}
      <div className="rounded-xl border border-[#262626] bg-[#171717] overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#141414] text-[#888888] border-b border-[#262626] font-mono">
              <tr>
                <th className="py-2.5 px-4">Run</th>
                <th className="py-2.5 px-4">Algorithm & Lineage</th>
                <th className="py-2.5 px-4">Author</th>
                <th className="py-2.5 px-4">Compute Node</th>
                <th className="py-2.5 px-4">Hardware Telemetry</th>
                <th className="py-2.5 px-4">Threat Signature</th>
                <th className="py-2.5 px-4">Similarity</th>
                <th className="py-2.5 px-4">DB Trigger Status</th>
                <th className="py-2.5 px-4">Mitigation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#222222]">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-[#888888] font-mono text-xs">
                    Loading records from MySQL database...
                  </td>
                </tr>
              ) : displayThreats.length > 0 ? (
                displayThreats.map((row, idx) => {
                  const isQuarantined = quarantinedNodes.has(row.node_id);
                  const isTerminated = row.execution_status?.toLowerCase() === "terminated" || row.alert_level === "Critical";
                  return (
                    <tr
                      key={row.detection_id || idx}
                      className="hover:bg-[#1c1c1c] transition-colors"
                    >
                      <td className="py-3 px-4 font-mono font-medium text-white">
                        #{row.run_id}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-semibold text-white">{row.algo_name}</div>
                        <div className="text-[11px] text-[#707070] font-mono">
                          {row.classification_result}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="text-[#ededed]">{row.developer_name}</div>
                        <div className="text-[10px] text-[#707070] font-mono">{row.team}</div>
                      </td>
                      <td className="py-3 px-4 font-mono">
                        <span className="text-[#a0a0a0]">{row.hostname}</span>
                        {isQuarantined && (
                          <span className="ml-2 text-[9px] px-1.5 py-0.2 rounded bg-[#2c1313] text-[#f87171] border border-[#482020] font-bold uppercase">
                            Quarantined
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 font-mono text-[11px]">
                        <div className="text-[#f87171]">IPC: {row.ipc_ratio || "0.62"}</div>
                        <div className="text-[#fb923c]">
                          Cache Miss: {row.cache_miss_rate || "36.5"}%
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded bg-[#241313] text-[#f87171] border border-[#3e1f1f] font-mono text-[11px]">
                          {row.detected_threat_signature}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono font-bold text-[#f87171]">
                        {row.similarity_score}%
                      </td>
                      <td className="py-3 px-4 font-mono">
                        {isTerminated ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-[#331111] text-[#f87171] border border-[#552020]">
                            Auto-Terminated
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-[#102a1d] text-[#3ecf8e] border border-[#1b4d36]">
                            Active / Monitored
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <button
                          onClick={() => onQuarantineNode(row.node_id || idx + 1, row.hostname)}
                          disabled={isQuarantined}
                          className={`px-2.5 py-1 rounded text-[11px] font-mono font-semibold transition-all flex items-center gap-1.5 ${
                            isQuarantined
                              ? "bg-[#222222] text-[#606060] cursor-not-allowed border border-[#2a2a2a]"
                              : "bg-[#251515] hover:bg-[#341b1b] text-[#f87171] border border-[#482424]"
                          }`}
                        >
                          <ShieldAlert className="w-3 h-3" />
                          <span>{isQuarantined ? "Quarantined" : "Quarantine Host"}</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-[#707070] font-mono text-xs">
                    No threat entries matching current filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Real SQL-Driven Pagination Bar */}
        <div className="flex items-center justify-between px-4 py-3 bg-[#141414] border-t border-[#262626] text-xs font-mono">
          <div className="text-[#888888]">
            Showing <span className="text-white font-medium">{(page - 1) * pageSize + 1}</span> to{" "}
            <span className="text-white font-medium">
              {Math.min(page * pageSize, totalRecords)}
            </span>{" "}
            of <span className="text-white font-semibold">{totalRecords.toLocaleString()}</span> entries
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1 || loading}
              className="p-1 rounded border border-[#2a2a2a] bg-[#1a1a1a] text-[#ededed] hover:bg-[#252525] disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-[#a0a0a0] px-1">
              Page <span className="text-white font-semibold">{page}</span> of {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages || loading}
              className="p-1 rounded border border-[#2a2a2a] bg-[#1a1a1a] text-[#ededed] hover:bg-[#252525] disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

