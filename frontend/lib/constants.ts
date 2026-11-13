export const API_BASE = "http://localhost:8000/api";

export type RoleType = "sec_admin" | "sec_analyst";

export interface SystemStats {
  total_runs: number;
  total_fingerprints: number;
  total_algorithms: number;
  total_nodes: number;
  critical_threats: number;
  high_threats: number;
  alert_distribution: { alert_level: string; count: number }[];
  architecture_distribution: { cpu_architecture: string; runs: number; avg_ipc: number }[];
  vector_db_size: number;
  graph_entities: number;
}

export interface AnomalyRecord {
  detection_id: number;
  run_id: number;
  node_id: number;
  algo_name: string;
  developer_name: string;
  team: string;
  hostname: string;
  detected_threat_signature: string;
  similarity_score: number;
  alert_level: string;
  classification_result: string;
  signature_hash: string;
  ipc_ratio?: number;
  cache_miss_rate?: number;
  branch_misprediction_rate?: number;
  peak_memory_mb?: number;
  execution_status?: string;
}

export interface GraphNode {
  id: string;
  label: string;
  properties: Record<string, any>;
}

export interface GraphData {
  root_node: GraphNode;
  traversal_depth: number;
  total_compromised_nodes: number;
  nodes: GraphNode[];
}

export interface VectorMatch {
  vector_id: string;
  similarity_score: number;
  distance: number;
  raw_vector: number[];
  metadata: {
    type: string;
    category?: string;
    name?: string;
    algo_name?: string;
    classification?: string;
    hostname?: string;
  };
}

export const SQL_PRESETS: Record<
  string,
  { label: string; tag: string; desc: string; query: string }
> = {
  recursive_cte: {
    label: "Algorithm Lineage & Mutation",
    tag: "Recursive CTE",
    desc: "Traverses parent-child polymorphic algorithm derivations to depth 10",
    query: `-- 1. Recursive CTE: Polymorphic Algorithm Lineage
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
  },
  correlated_subquery: {
    label: "Memory Consumers Above Average",
    tag: "Correlated Subquery",
    desc: "Identifies runs using greater peak memory than average for that language",
    query: `-- 2. Correlated Subquery: Peak Memory Exceeding Language Average
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
  },
  nested_subquery: {
    label: "Hosts Running Critical Malware",
    tag: "Nested Subquery",
    desc: "Multi-level subquery identifying compute nodes hosting cryptojackers",
    query: `-- 3. Nested Subquery: Compute nodes running critical rogue code
SELECT node_id, hostname, ip_address, os_name
FROM compute_node
WHERE node_id IN (
    SELECT DISTINCT r.node_id
    FROM execution_run r
    WHERE r.run_id IN (
        SELECT f.run_id
        FROM fingerprint f
        WHERE f.fingerprint_id IN (
            SELECT dl.fingerprint_id
            FROM detection_log dl
            WHERE dl.alert_level = 'Critical' AND dl.classification_result = 'Malicious_Cryptojacking'
        )
    )
)
LIMIT 10;`,
  },
  multi_join: {
    label: "6-Table Architecture Aggregates",
    tag: "Multi-Table Join",
    desc: "Aggregates runs, memory, and mean IPC across CPU architecture families",
    query: `-- 4. Multi-Table Join: Cross-Entity Microarchitectural Counters
SELECT 
    cn.cpu_architecture,
    COUNT(er.run_id) AS total_executions,
    ROUND(SUM(er.peak_memory_mb), 2) AS total_memory_mb,
    ROUND(AVG(fp.ipc_ratio), 3) AS mean_ipc,
    ROUND(AVG(fp.cache_miss_rate), 2) AS mean_cache_miss_pct
FROM compute_node cn
JOIN execution_run er ON cn.node_id = er.node_id
JOIN fingerprint fp ON er.run_id = fp.run_id
GROUP BY cn.cpu_architecture
ORDER BY total_memory_mb DESC;`,
  },
  team_cte: {
    label: "Team Threat Density Ranking",
    tag: "Non-Recursive CTE",
    desc: "Ranks engineering teams by frequency of critical threat injections",
    query: `-- 5. Non-Recursive CTE: Team-Level Threat Density
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
  },
  stored_procedure: {
    label: "Stored Procedure Execution",
    tag: "Stored Procedure",
    desc: "Invokes GetRunFingerprintProfile for an execution trace",
    query: `CALL GetRunFingerprintProfile(1);`,
  },
  stored_function: {
    label: "Stored Deterministic Function",
    tag: "Stored Function",
    desc: "Calculates mathematical percentage deviation from golden baseline",
    query: `SELECT fingerprint_id, ipc_ratio, CalculateIPCDeviation(fingerprint_id) AS deviation_score_pct
FROM fingerprint
LIMIT 10;`,
  },
  trigger_test: {
    label: "Negative IPC Validation Violation",
    tag: "Trigger Integrity",
    desc: "Triggers trg_validate_fingerprint_bounds rollback on negative IPC",
    query: `-- 8. Testing BEFORE INSERT Trigger: trg_validate_fingerprint_bounds
-- Intentionally invalid negative IPC value to demonstrate constraint rejection
INSERT INTO fingerprint (run_id, ipc_ratio, cache_miss_rate, branch_misprediction_rate, signature_hash)
VALUES (99999, -1.25, 25.0, 10.0, 'dummyhash12345678901234567890123456789012345678901234567890123456');`,
  },
  rbac_test: {
    label: "DROP TABLE (Security Denial)",
    tag: "RBAC Gating",
    desc: "SecOps analyst gets immediate 403 Forbidden on DDL mutation",
    query: `-- 9. RBAC Denial Test: Dropping table is restricted to sec_admin
DROP TABLE IF EXISTS test_audit_logs;`,
  },
};

