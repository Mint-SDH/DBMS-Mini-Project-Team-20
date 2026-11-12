-- ====================================================================
-- ALGORITHMIC EXECUTION FINGERPRINTING & RUNTIME THREAT DETECTION
-- Relational Analytical Queries & Advanced SQL Suite
-- Author: Shashank A (PES2UG24CS461) | Group 20
-- Engine: MySQL 8.0+
-- Database: algo_fingerprint_db
-- ====================================================================

USE algo_fingerprint_db;

-- ====================================================================
-- 1. Simple Aggregates & GROUP BY
-- Compute mean IPC, average cache miss percentage, and total runs grouped by CPU architecture
-- ====================================================================
SELECT 
    cn.cpu_architecture,
    COUNT(DISTINCT r.run_id) AS profiled_runs,
    ROUND(AVG(f.ipc_ratio), 3) AS mean_ipc,
    ROUND(AVG(f.cache_miss_rate), 2) AS mean_cache_miss_pct,
    ROUND(AVG(r.peak_memory_mb), 2) AS mean_peak_memory_mb
FROM COMPUTE_NODE cn
JOIN EXECUTION_RUN r ON cn.node_id = r.node_id
JOIN FINGERPRINT f ON r.run_id = f.run_id
GROUP BY cn.cpu_architecture;

-- ====================================================================
-- 2. UPDATE & Transactional Isolation (ACID Demonstration)
-- Safely test an experimental baseline update within an isolated transaction boundary
-- ====================================================================
START TRANSACTION;
UPDATE BASELINE_PATTERN 
SET expected_ipc = 5.00 
WHERE baseline_id = 1;

SELECT baseline_id, pattern_name, expected_ipc 
FROM BASELINE_PATTERN 
WHERE baseline_id = 1;

ROLLBACK;

-- ====================================================================
-- 3. DELETE & Cascading Operations
-- Safely purge obsolete failed runs while verifying cascading cleanup across FINGERPRINT & DETECTION_LOG
-- ====================================================================
-- Preview tuples candidate for cascading removal:
SELECT er.run_id, er.execution_status, er.peak_memory_mb, fp.fingerprint_id
FROM EXECUTION_RUN er
LEFT JOIN FINGERPRINT fp ON er.run_id = fp.run_id
WHERE er.execution_status = 'Failed' AND er.peak_memory_mb < 200.00
LIMIT 10;

-- ====================================================================
-- 4. Correlated Subquery
-- Identify execution runs consuming greater peak memory than average for their language
-- ====================================================================
SELECT 
    a1.algo_id, 
    a1.algo_name, 
    a1.language, 
    er1.run_id, 
    er1.peak_memory_mb
FROM ALGORITHM a1
JOIN EXECUTION_RUN er1 ON a1.algo_id = er1.algo_id
WHERE er1.peak_memory_mb > (
    SELECT AVG(er2.peak_memory_mb)
    FROM ALGORITHM a2
    JOIN EXECUTION_RUN er2 ON a2.algo_id = er2.algo_id
    WHERE a2.language = a1.language
)
ORDER BY er1.peak_memory_mb DESC
LIMIT 15;

-- ====================================================================
-- 5. Nested Subquery (Multi-level Subquery without outer JOIN)
-- Find all compute nodes that hosted critical cryptojacking malware runs
-- ====================================================================
SELECT node_id, hostname, ip_address, os_name
FROM COMPUTE_NODE
WHERE node_id IN (
    SELECT DISTINCT r.node_id
    FROM EXECUTION_RUN r
    WHERE r.run_id IN (
        SELECT f.run_id
        FROM FINGERPRINT f
        WHERE f.fingerprint_id IN (
            SELECT dl.fingerprint_id
            FROM DETECTION_LOG dl
            WHERE dl.alert_level = 'Critical' 
              AND dl.classification_result = 'Malicious_Cryptojacking'
        )
    )
);

-- ====================================================================
-- 6. Multi-Table Join Query
-- Aggregate total memory allocated and average IPC across compute node architectures
-- ====================================================================
SELECT 
    cn.cpu_architecture,
    COUNT(er.run_id) AS total_executions,
    ROUND(SUM(er.peak_memory_mb), 2) AS total_memory_allocated_mb,
    ROUND(AVG(fp.ipc_ratio), 3) AS average_ipc_ratio
FROM COMPUTE_NODE cn
JOIN EXECUTION_RUN er ON cn.node_id = er.node_id
JOIN FINGERPRINT fp ON er.run_id = fp.run_id
GROUP BY cn.cpu_architecture
ORDER BY total_memory_allocated_mb DESC;

-- ====================================================================
-- 7. Common Table Expressions (CTE)
-- Rank engineering teams by threat density percentage and average congruence
-- ====================================================================
WITH TeamThreatMetrics AS (
    SELECT 
        d.team,
        COUNT(DISTINCT r.run_id) AS total_runs,
        SUM(CASE WHEN dl.alert_level = 'Critical' THEN 1 ELSE 0 END) AS critical_alerts,
        ROUND(AVG(dl.similarity_score), 2) AS avg_congruence
    FROM DEVELOPER d
    JOIN ALGORITHM a ON d.dev_id = a.dev_id
    JOIN EXECUTION_RUN r ON a.algo_id = r.algo_id
    JOIN FINGERPRINT f ON r.run_id = f.run_id
    JOIN DETECTION_LOG dl ON f.fingerprint_id = dl.fingerprint_id
    GROUP BY d.team
)
SELECT 
    team,
    total_runs,
    critical_alerts,
    avg_congruence,
    ROUND((critical_alerts / total_runs) * 100, 2) AS threat_density_pct
FROM TeamThreatMetrics
ORDER BY threat_density_pct DESC;

-- ====================================================================
-- 8. Recursive CTE: Algorithm Lineage & Polymorphic Mutation Hierarchy
-- Recursively traverse parent-child mutation chains from root base algorithms
-- ====================================================================
WITH RECURSIVE AlgoLineage AS (
    -- Anchor Member: Root algorithms without parents
    SELECT 
        algo_id, 
        algo_name, 
        version, 
        parent_algo_id, 
        1 AS lineage_depth, 
        CAST(algo_name AS CHAR(500)) AS lineage_path
    FROM ALGORITHM
    WHERE parent_algo_id IS NULL AND algo_id IN (2, 4, 6, 14)
    
    UNION ALL
    
    -- Recursive Member: Iterative child algorithms derived from parents
    SELECT 
        a.algo_id, 
        a.algo_name, 
        a.version, 
        a.parent_algo_id, 
        al.lineage_depth + 1, 
        CONCAT(al.lineage_path, ' -> ', a.algo_name)
    FROM ALGORITHM a
    JOIN AlgoLineage al ON a.parent_algo_id = al.algo_id
    WHERE al.lineage_depth < 10
)
SELECT algo_id, lineage_depth, lineage_path 
FROM AlgoLineage 
ORDER BY lineage_path;

