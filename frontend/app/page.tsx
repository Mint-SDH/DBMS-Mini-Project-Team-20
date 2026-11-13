"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/layout/Header";
import { Sidebar, TabType } from "@/components/layout/Sidebar";
import { OverviewView } from "@/components/dashboard/OverviewView";
import { ThreatsView } from "@/components/threats/ThreatsView";
import { SqlRunnerView } from "@/components/sql/SqlRunnerView";
import { GraphView } from "@/components/graph/GraphView";
import { VectorView } from "@/components/vector/VectorView";
import { RubricView } from "@/components/rubric/RubricView";
import { RoleType, SystemStats, AnomalyRecord, API_BASE } from "@/lib/constants";
import { CheckCircle2, AlertTriangle, XCircle, Info } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>("dashboard");
  const [role, setRole] = useState<RoleType>("sec_admin");
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [threats, setThreats] = useState<AnomalyRecord[]>([]);
  const [quarantinedNodes, setQuarantinedNodes] = useState<Set<number>>(new Set());
  const [alert, setAlert] = useState<{ type: "success" | "error" | "info"; msg: string } | null>(
    null
  );

  const showAlert = (type: "success" | "error" | "info", msg: string) => {
    setAlert({ type, msg });
  };

  const fetchInitialData = async () => {
    try {
      const [statsRes, threatsRes] = await Promise.all([
        fetch(`${API_BASE}/dashboard/stats`),
        fetch(`${API_BASE}/anomalies/critical?limit=100`),
      ]);

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
      if (threatsRes.ok) {
        const threatsData = await threatsRes.json();
        setThreats(threatsData.data || []);
      }
    } catch (err) {
      console.error("Data fetch error:", err);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  const handleQuarantineNode = async (nodeId: number, hostname: string) => {
    if (role === "sec_analyst") {
      showAlert(
        "error",
        "403 Forbidden: Role 'sec_analyst' lacks privilege to modify cluster state. Switch to 'sec_admin' to quarantine compute nodes."
      );
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/graph/quarantine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_id: nodeId, reason: "Manual SecOps Mitigation" }),
      });
      const data = await res.json();
      setQuarantinedNodes((prev) => new Set(prev).add(nodeId));
      showAlert(
        "success",
        `Compute node ${hostname} [ID: ${nodeId}] quarantined successfully. State updated across Graph and Relational boundaries.`
      );
    } catch (err: any) {
      showAlert("error", `Quarantine operation failed: ${err.message}`);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#121212] text-[#ededed] font-sans antialiased overflow-hidden">
      {/* Top Supabase-like Navbar */}
      <Header role={role} setRole={setRole} onAlert={showAlert} />

      {/* Main Multi-File Workspace */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          role={role}
          threatsCount={threats.length}
        />

        {/* Center Dynamic Tab Content Area */}
        <main className="flex-1 overflow-y-auto p-6 bg-[#121212] space-y-4">
          {/* Action Notification Alert Bar */}
          {alert && (
            <div
              className={`p-3.5 rounded-lg border text-xs font-mono flex items-center justify-between transition-all ${
                alert.type === "error"
                  ? "bg-[#251515] border-[#401f1f] text-[#f87171]"
                  : alert.type === "success"
                  ? "bg-[#182a20] border-[#204530] text-[#3ecf8e]"
                  : "bg-[#16202c] border-[#1e3447] text-[#60a5fa]"
              }`}
            >
              <div className="flex items-center gap-2">
                {alert.type === "error" ? (
                  <AlertTriangle className="w-4 h-4 flex-shrink-0 text-[#f87171]" />
                ) : (
                  <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-[#3ecf8e]" />
                )}
                <span>{alert.msg}</span>
              </div>
              <button
                onClick={() => setAlert(null)}
                className="text-[#888888] hover:text-white ml-2"
              >
                <XCircle className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Tab Views */}
          {activeTab === "dashboard" && (
            <OverviewView stats={stats} onNavigateToTab={setActiveTab} />
          )}

          {activeTab === "threats" && (
            <ThreatsView
              threats={threats}
              role={role}
              onQuarantineNode={handleQuarantineNode}
              quarantinedNodes={quarantinedNodes}
            />
          )}

          {activeTab === "sql" && <SqlRunnerView role={role} />}

          {activeTab === "graph" && <GraphView />}

          {activeTab === "vector" && <VectorView />}

          {activeTab === "rubric" && <RubricView />}
        </main>
      </div>
    </div>
  );
}
