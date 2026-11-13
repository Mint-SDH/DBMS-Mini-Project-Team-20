"use client";

import React from "react";
import {
  Database,
  Cpu,
  Activity,
  AlertTriangle,
  Binary,
  Share2,
  CheckCircle2,
  Flame,
  Layers,
  ArrowUpRight,
  Server,
} from "lucide-react";
import { SystemStats } from "@/lib/constants";

interface OverviewViewProps {
  stats: SystemStats | null;
  onNavigateToTab: (tab: any) => void;
}

export function OverviewView({ stats, onNavigateToTab }: OverviewViewProps) {
  const kpiData = [
    {
      title: "Profiled Execution Runs",
      value: stats ? stats.total_runs.toLocaleString() : "4,000",
      caption: "3,637 1:1 Microarchitectural Fingerprints",
      icon: Database,
      accent: "text-white",
      tag: "1:1 STRICT",
    },
    {
      title: "Critical Rogue Anomalies",
      value: stats ? stats.critical_threats.toLocaleString() : "827",
      caption: "Auto-Terminated by Trigger",
      icon: AlertTriangle,
      accent: "text-[#f87171]",
      tag: "TRIGGER ACTIVE",
    },
    {
      title: "5D Vector Index Size",
      value: stats ? stats.vector_db_size.toLocaleString() : "622",
      caption: "Cosine Similarity Metric Space",
      icon: Binary,
      accent: "text-[#3ecf8e]",
      tag: "k-NN ACTIVE",
    },
    {
      title: "Graph Database Entities",
      value: stats ? stats.graph_entities.toLocaleString() : "973",
      caption: "3,300 Multi-Hop Cypher Edges",
      icon: Share2,
      accent: "text-[#f59e0b]",
      tag: "NEO4J SCHEMA",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Title & Description */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#262626]">
        <div>
          <h2 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
            System Telemetry Overview
          </h2>
          <p className="text-xs text-[#888888] mt-0.5">
            Microarchitectural hardware performance counters across relational, graph, and vector database engines.
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded-md bg-[#1c1c1c] border border-[#2a2a2a] text-[#a0a0a0]">
            Database: <strong className="text-white">algo_fingerprint_db</strong>
          </span>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiData.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              className="p-4 rounded-xl bg-[#171717] border border-[#262626] hover:border-[#383838] transition-all relative overflow-hidden group shadow-sm"
            >
              <div className="flex items-center justify-between text-[#888888]">
                <span className="text-xs font-medium">{kpi.title}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#202020] border border-[#2c2c2c] text-[#888888]">
                  {kpi.tag}
                </span>
              </div>
              <div className={`text-2xl font-bold font-mono tracking-tight mt-2 ${kpi.accent}`}>
                {kpi.value}
              </div>
              <div className="text-[11px] text-[#707070] mt-2 flex items-center gap-1.5 font-mono">
                <CheckCircle2 className="w-3 h-3 text-[#3ecf8e]" />
                <span>{kpi.caption}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Architecture Distribution & Severity Classifier */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Hardware Architecture Breakdown */}
        <div className="p-5 rounded-xl bg-[#171717] border border-[#262626] space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <Cpu className="w-3.5 h-3.5 text-[#3ecf8e]" />
              Heterogeneous Hardware Architectures
            </h3>
            <span className="text-[11px] font-mono text-[#707070]">35 Cluster Nodes</span>
          </div>

          <div className="space-y-2.5">
            {stats?.architecture_distribution?.map((item, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg bg-[#141414] border border-[#222222] flex items-center justify-between"
              >
                <div>
                  <div className="text-xs font-semibold text-white font-mono">{item.cpu_architecture}</div>
                  <div className="text-[11px] text-[#707070] mt-0.5">
                    {item.runs.toLocaleString()} execution traces profiled
                  </div>
                </div>
                <div className="text-right font-mono">
                  <div className="text-xs font-bold text-[#3ecf8e]">Mean IPC: {item.avg_ipc}</div>
                  <div className="text-[10px] text-[#707070]">Expected Range: 0.50 - 3.50</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Security Alert Severity Breakdown */}
        <div className="p-5 rounded-xl bg-[#171717] border border-[#262626] space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <AlertTriangle className="w-3.5 h-3.5 text-[#f87171]" />
              Detection Log Severity Classification
            </h3>
            <span className="text-[11px] font-mono text-[#707070]">9,078 Total Logs</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {stats?.alert_distribution?.map((alert, idx) => {
              const alertThemes: Record<string, { bg: string; text: string; border: string }> = {
                Critical: { bg: "bg-[#281414]", text: "text-[#f87171]", border: "border-[#401e1e]" },
                High: { bg: "bg-[#291b11]", text: "text-[#fb923c]", border: "border-[#452818]" },
                Medium: { bg: "bg-[#292212]", text: "text-[#fbbf24]", border: "border-[#483a1b]" },
                Low: { bg: "bg-[#142028]", text: "text-[#60a5fa]", border: "border-[#1e3445]" },
                Info: { bg: "bg-[#181818]", text: "text-[#a3a3a3]", border: "border-[#2a2a2a]" },
              };
              const theme = alertThemes[alert.alert_level] || alertThemes.Info;
              return (
                <div
                  key={idx}
                  className={`p-3 rounded-lg border ${theme.bg} ${theme.border} space-y-1`}
                >
                  <div className={`text-[10px] font-mono font-semibold uppercase ${theme.text}`}>
                    {alert.alert_level}
                  </div>
                  <div className="text-lg font-bold font-mono text-white">
                    {alert.count.toLocaleString()}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

