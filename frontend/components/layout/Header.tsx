"use client";

import React from "react";
import {
  ShieldAlert,
  Database,
  Lock,
  UserCheck,
  Activity,
  Server,
  Terminal,
  Share2,
  Binary,
  Layers,
  Sparkles,
  ExternalLink,
} from "lucide-react";
import { RoleType } from "@/lib/constants";

interface HeaderProps {
  role: RoleType;
  setRole: (r: RoleType) => void;
  onAlert: (type: "success" | "error" | "info", msg: string) => void;
}

export function Header({ role, setRole, onAlert }: HeaderProps) {
  return (
    <header className="h-14 border-b border-[#262626] bg-[#171717] px-5 flex items-center justify-between flex-shrink-0 z-30">
      {/* Brand & Project Info */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-[#222222] border border-[#2e2e2e] flex items-center justify-center text-[#3ecf8e]">
          <ShieldAlert className="w-4 h-4 text-[#3ecf8e]" />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold tracking-tight text-white flex items-center gap-1.5">
            ExecutionGuard
          </span>
          <span className="text-xs text-[#888888] font-mono">/</span>
          <span className="text-xs font-mono text-[#888888] px-2 py-0.5 rounded bg-[#1e1e1e] border border-[#2e2e2e]">
            algo_fingerprint_db
          </span>
          <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-[#1b2b23] text-[#3ecf8e] border border-[#214332] hidden md:inline-block">
            MySQL 8.0 • Neo4j • 5D Vector
          </span>
        </div>
      </div>

      {/* RBAC Role Switcher & Status */}
      <div className="flex items-center gap-3">
        {/* Role Toggle Button */}
        <div className="flex items-center bg-[#1f1f1f] border border-[#2e2e2e] rounded-lg p-0.5 text-xs font-mono">
          <button
            onClick={() => {
              setRole("sec_admin");
              onAlert(
                "info",
                "Switched context to 'sec_admin' (Full DBA & SecOps Privileges: DDL, Quarantine, Mutation enabled)."
              );
            }}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md transition-all ${
              role === "sec_admin"
                ? "bg-[#2a2a2a] text-[#3ecf8e] font-semibold shadow-sm"
                : "text-[#888888] hover:text-[#ededed]"
            }`}
          >
            <Lock className="w-3 h-3" />
            <span>sec_admin</span>
          </button>
          <button
            onClick={() => {
              setRole("sec_analyst");
              onAlert(
                "info",
                "Switched context to 'sec_analyst' (Security Analyst: Read/Insert permitted, DDL/Quarantine restricted)."
              );
            }}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md transition-all ${
              role === "sec_analyst"
                ? "bg-[#2a2a2a] text-[#3ecf8e] font-semibold shadow-sm"
                : "text-[#888888] hover:text-[#ededed]"
            }`}
          >
            <UserCheck className="w-3 h-3" />
            <span>sec_analyst</span>
          </button>
        </div>

        {/* Database User Status Pill */}
        <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-[#888888] pl-2 border-l border-[#262626]">
          <span className="w-2 h-2 rounded-full bg-[#3ecf8e]"></span>
          <span>{role === "sec_admin" ? "admin_user" : "analyst_user"}@localhost</span>
        </div>
      </div>
    </header>
  );
}
