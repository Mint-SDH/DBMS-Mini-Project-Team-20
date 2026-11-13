"use client";

import React from "react";
import {
  Activity,
  AlertTriangle,
  Share2,
  Binary,
  Terminal,
  Award,
  Layers,
  CheckCircle2,
  Lock,
} from "lucide-react";
import { RoleType } from "@/lib/constants";

export type TabType = "dashboard" | "threats" | "graph" | "vector" | "sql" | "rubric";

interface SidebarProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  role: RoleType;
  threatsCount: number;
}

export function Sidebar({ activeTab, setActiveTab, role, threatsCount }: SidebarProps) {
  const navItems: { id: TabType; label: string; icon: any; count?: string }[] = [
    { id: "dashboard", label: "Overview & Stats", icon: Activity },
    { id: "threats", label: "Threat Audit Log", icon: AlertTriangle, count: "Relational" },
    { id: "sql", label: "SQL & Query Runner", icon: Terminal, count: "ACID" },
    { id: "graph", label: "Threat Blast Radius", icon: Share2, count: "Neo4j" },
    { id: "vector", label: "Vector k-NN", icon: Binary, count: "5D Space" },
    { id: "rubric", label: "Rubric Compliance", icon: Award, count: "46/46" },
  ];

  return (
    <aside className="w-64 border-r border-[#262626] bg-[#141414] flex flex-col justify-between p-3 flex-shrink-0 select-none">
      {/* Navigation Section */}
      <div className="space-y-4">
        <div className="px-2 pt-1 text-[11px] font-mono uppercase tracking-wider text-[#707070] font-semibold">
          Database Management
        </div>

        <nav className="space-y-0.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-2.5 py-2 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? "bg-[#222222] text-white font-semibold shadow-sm border border-[#2e2e2e]"
                    : "text-[#999999] hover:bg-[#1a1a1a] hover:text-[#ededed] border border-transparent"
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? "text-[#3ecf8e]" : "text-[#707070]"}`} />
                  <span className="truncate">{item.label}</span>
                </div>
                {item.count && (
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.2 rounded border flex-shrink-0 ml-1.5 ${
                      isActive
                        ? "bg-[#1b2b23] text-[#3ecf8e] border-[#214332]"
                        : "bg-[#1f1f1f] text-[#707070] border-[#2a2a2a]"
                    }`}
                  >
                    {item.count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Security Context & Author Footer */}
      <div className="space-y-3 pt-3 border-t border-[#222222]">
        <div className="p-3 rounded-lg bg-[#181818] border border-[#262626] space-y-1.5 text-xs">
          <div className="flex items-center justify-between text-[#888888] font-mono text-[11px]">
            <span className="flex items-center gap-1.5">
              <Lock className="w-3 h-3 text-[#3ecf8e]" />
              Role Privilege
            </span>
            <span className="text-[#3ecf8e] font-semibold">{role}</span>
          </div>
          <p className="text-[#707070] text-[11px] leading-relaxed">
            {role === "sec_admin"
              ? "Full authority: DDL, TRUNCATE, schema mutation, quarantine actions."
              : "Read/Insert permitted. DDL/DROP restricted to enforce integrity."}
          </p>
        </div>

        <div className="px-2 text-[10px] font-mono text-[#666666] flex flex-col gap-0.5">
          <span>PES University • Group 20</span>
          <span>PES2UG24CS446 & PES2UG24CS461</span>
        </div>
      </div>
    </aside>
  );
}

