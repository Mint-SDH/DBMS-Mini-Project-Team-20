"use client";

import React, { useState } from "react";
import {
  Terminal,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Lock,
  Copy,
  Check,
} from "lucide-react";
import { SQL_PRESETS, RoleType, API_BASE } from "@/lib/constants";

interface SqlRunnerViewProps {
  role: RoleType;
}

export function SqlRunnerView({ role }: SqlRunnerViewProps) {
  const [selectedKey, setSelectedKey] = useState("recursive_cte");
  const [queryText, setQueryText] = useState(SQL_PRESETS.recursive_cte.query);
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleSelectPreset = (key: string) => {
    setSelectedKey(key);
    setQueryText(SQL_PRESETS[key].query);
    setError(null);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(queryText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExecute = async () => {
    try {
      setExecuting(true);
      setError(null);
      setResult(null);

      const res = await fetch(`${API_BASE}/queries/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: queryText, role }),
      });

      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Query execution failed.");
      } else {
        setResult(data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to connect to backend SQL engine.");
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#262626]">
        <div>
          <h2 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
            SQL & Advanced Query Runner
          </h2>
          <p className="text-xs text-[#888888] mt-0.5">
            Execute Recursive CTEs, Correlated Subqueries, Stored Procedures, Functions, and Triggers with dynamic RBAC gating.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="text-[#707070]">Active User:</span>
          <span className="px-2 py-0.5 rounded bg-[#1e1e1e] border border-[#2e2e2e] text-[#3ecf8e]">
            {role === "sec_admin" ? "admin_user (sec_admin)" : "analyst_user (sec_analyst)"}
          </span>
        </div>
      </div>

      {/* Preset Selector Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {Object.entries(SQL_PRESETS).map(([key, item]) => (
          <button
            key={key}
            onClick={() => handleSelectPreset(key)}
            className={`p-2.5 rounded-lg text-left border transition-all ${
              selectedKey === key
                ? "bg-[#1d2b23] border-[#29543e] text-white"
                : "bg-[#171717] border-[#262626] text-[#888888] hover:text-[#ededed] hover:border-[#383838]"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-white truncate">{item.label}</span>
              <span
                className={`text-[9px] font-mono px-1.5 py-0.2 rounded border ${
                  selectedKey === key
                    ? "bg-[#214332] text-[#3ecf8e] border-[#29543e]"
                    : "bg-[#202020] text-[#707070] border-[#2c2c2c]"
                }`}
              >
                {item.tag}
              </span>
            </div>
            <div className="text-[10px] text-[#707070] truncate mt-1">{item.desc}</div>
          </button>
        ))}
      </div>

      {/* SQL Editor Window */}
      <div className="rounded-xl border border-[#262626] bg-[#171717] overflow-hidden shadow-sm space-y-2 p-3">
        <div className="flex items-center justify-between px-2 pt-1">
          <span className="text-[11px] font-mono text-[#707070] uppercase tracking-wider font-semibold">
            SQL Query Input
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="text-xs text-[#888888] hover:text-white flex items-center gap-1 font-mono px-2 py-0.5 rounded bg-[#1f1f1f] border border-[#2a2a2a]"
            >
              {copied ? <Check className="w-3 h-3 text-[#3ecf8e]" /> : <Copy className="w-3 h-3" />}
              <span>{copied ? "Copied" : "Copy"}</span>
            </button>
            <button
              onClick={() => handleSelectPreset(selectedKey)}
              className="text-xs text-[#888888] hover:text-white flex items-center gap-1 font-mono px-2 py-0.5 rounded bg-[#1f1f1f] border border-[#2a2a2a]"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          </div>
        </div>

        <textarea
          value={queryText}
          onChange={(e) => setQueryText(e.target.value)}
          rows={7}
          className="w-full bg-[#121212] border border-[#262626] rounded-lg p-3 font-mono text-xs text-[#3ecf8e] focus:outline-none focus:border-[#3ecf8e] transition-all resize-y"
        />

        <div className="flex items-center justify-between pt-1">
          <span className="text-[11px] text-[#707070] font-mono">
            {role === "sec_analyst" && (
              <span className="text-[#f87171]">Notice: DDL statements (DROP, ALTER, TRUNCATE) will be rejected under sec_analyst role.</span>
            )}
          </span>
          <button
            onClick={handleExecute}
            disabled={executing}
            className="px-4 py-2 rounded-lg bg-[#3ecf8e] hover:bg-[#34b27b] text-[#121212] font-mono font-bold text-xs flex items-center gap-2 transition-all shadow-sm disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{executing ? "Running..." : "Run Query"}</span>
          </button>
        </div>
      </div>

      {/* Query Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-[#241313] border border-[#401f1f] text-[#f87171] text-xs font-mono space-y-1">
          <div className="font-bold flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4 text-[#f87171]" />
            <span>Execution Blocked / Constraint Violation:</span>
          </div>
          <div className="text-[11px] text-[#fca5a5] pl-5">{error}</div>
        </div>
      )}

      {/* Query Result Table */}
      {result && (
        <div className="rounded-xl border border-[#262626] bg-[#171717] overflow-hidden shadow-sm p-4 space-y-3">
          <div className="flex items-center justify-between text-xs font-mono text-[#888888]">
            <span>
              Query Status: <strong className="text-[#3ecf8e]">Success</strong>
            </span>
            <span>Returned {result.count || result.affected_rows || 0} row(s)</span>
          </div>

          {result.rows && result.rows.length > 0 ? (
            <div className="overflow-x-auto max-h-80 border border-[#222222] rounded-lg">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#141414] text-[#888888] border-b border-[#262626] font-mono">
                  <tr>
                    {Object.keys(result.rows[0]).map((key, i) => (
                      <th key={i} className="py-2.5 px-3">
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#222222] font-mono">
                  {result.rows.map((row: any, idx: number) => (
                    <tr key={idx} className="hover:bg-[#1a1a1a]">
                      {Object.values(row).map((val: any, j: number) => (
                        <td key={j} className="py-2 px-3 text-[#ededed]">
                          {val !== null ? String(val) : "NULL"}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-xs text-[#3ecf8e] font-mono">
              {result.message || "Statement executed successfully with zero returned rows."}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
