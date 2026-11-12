# Algorithmic Execution Fingerprinting - Synthetic Dataset Guide

**DBMS Mini Project | Group 20**  
**Team Members:**  
- Sanyam Deven Hiran (PES2UG24CS446)  
- Shashank A (PES2UG24CS461)  
**Database Engine:** MySQL 8.0+  
**Database Name:** `algo_fingerprint_db`

---

## 1. Domain Context & Architectural Archetypes

Algorithmic execution fingerprinting tracks low-level runtime behavioral metrics (hardware performance counters such as Instructions Per Cycle [IPC], cache miss rates, and branch mispredictions) produced by an executing process.

The synthetic data generation engine models **5 strict domain archetypes**:

| Archetype | Linked Golden Baseline | Target IPC | Cache Miss Rate | Branch Mispred Rate | Peak Memory | Expected Classification |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **1. HPC Matrix / Math** | `Matrix_Multiplication_BLAS` | **2.500 – 3.500** | **1.50% – 5.00%** | **0.50% – 2.00%** | High (> 1 GB) | `Verified_Safe` (`Info`) |
| **2. Cryptojacking Malware** | `Crypto_Miner_XMRig` | **0.500 – 0.850** | **30.00% – 48.00%** | **12.00% – 22.00%** | High (> 2 GB) | `Malicious_Cryptojacking` (`Critical`) |
| **3. Reconnaissance Probe** | `Port_Scan_SYN_Flood` | **0.300 – 0.600** | **20.00% – 35.00%** | **10.00% – 18.00%** | Low (< 256 MB) | `Port_Scan_Detected` (`High`) |
| **4. Financial HFT** | `TWAP_Order_Slicing` | **1.200 – 1.700** | **5.00% – 9.00%** | **2.00% – 5.00%** | Moderate (256M–4G) | `Verified_Safe` (`Info`) |
| **5. Sorting & Utilities** | `QuickSort_In_Memory` | **1.900 – 2.400** | **6.00% – 11.00%** | **1.50% – 4.00%** | Moderate (128M–4G) | `Verified_Safe` (`Info`) |

---

## 2. Relational Architecture & Topological Order

```text
  [DEVELOPER] ──────────┐
                        ▼
                  [ALGORITHM] ──────────┐
                                        ▼
  [COMPUTE_NODE] ────────────────> [EXECUTION_RUN]
                                        │ (1:1)
                                        ▼
                                  [FINGERPRINT] ────────┐
                                                        ▼
  [BASELINE_PATTERN] ───────────────────────────> [DETECTION_LOG]
```

### Table Specifications & Generated Counts:

1. **`DEVELOPER` (75 rows)**: Members across `Core Systems`, `Security & HFT`, `Infrastructure`, `AI & Quant`, and `Compiler Toolchain`. Unique emails (`name.surname@techcorp.io`).
2. **`COMPUTE_NODE` (35 rows)**: Server instances (`x86_64`, `ARM64`) with unique hostnames (`node-<region>-<rack>-<slot>`) and unique private CIDR IPs (`10.x.x.x` / `192.168.10.x`).
3. **`BASELINE_PATTERN` (25 rows)**: Golden architectural reference profiles.
4. **`ALGORITHM` (300 rows)**: ~4 algorithms per developer across `C++`, `Rust`, `C`, `Go`, and `Python` with semantic versioning (`v1.0.0`, etc.).
5. **`EXECUTION_RUN` (4,000 rows)**: Traces within past 30 days (`Completed`, `Terminated`, `Running`, `Failed`). Strict chronological constraint: `end_time > start_time`.
6. **`FINGERPRINT` (3,637 rows)**: **Strict 1:1** with completed/terminated execution runs. Deterministic 64-character SHA-256 signature hash.
7. **`DETECTION_LOG` (9,078 rows)**: Primary congruent comparisons against matched baseline + cross-validation against contrasting baselines.

---

## 3. How to Insert Into MySQL

### Method 1: Using the Automated Python Inserter (Recommended)
```powershell
python insert_to_db.py
```
- Prompts for MySQL password.
- Prompts whether to clear existing partial data (`y`).
- Executes all 80 batched statements wrapped in transactions.
- Verifies row counts for all 7 tables upon completion.

### Method 2: Using MySQL Command Line (PowerShell)
```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p algo_fingerprint_db -e "source algo_fingerprint_data.sql"
```

### Method 3: Using MySQL Workbench
1. Open MySQL Workbench and connect to `algo_fingerprint_db`.
2. Press `Ctrl + Shift + O` and select `algo_fingerprint_data.sql`.
3. Press `Ctrl + Shift + Enter` to execute.

### Method 4: High-Speed Bulk Load via CSV (Mode B)
Individual CSV files are generated in `csv_data/`:
```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" --local-infile=1 -u root -p algo_fingerprint_db -e "source load_csv.sql"
```

---

## 4. Verification & Analytical Queries for Mini-Project Demo

### Query 1: Verify Table Counts & 1:1 Fingerprint Integrity
```sql
USE algo_fingerprint_db;

SELECT 'DEVELOPER' AS table_name, COUNT(*) AS total_rows FROM DEVELOPER
UNION ALL
SELECT 'COMPUTE_NODE', COUNT(*) FROM COMPUTE_NODE
UNION ALL
SELECT 'BASELINE_PATTERN', COUNT(*) FROM BASELINE_PATTERN
UNION ALL
SELECT 'ALGORITHM', COUNT(*) FROM ALGORITHM
UNION ALL
SELECT 'EXECUTION_RUN', COUNT(*) FROM EXECUTION_RUN
UNION ALL
SELECT 'FINGERPRINT', COUNT(*) FROM FINGERPRINT
UNION ALL
SELECT 'DETECTION_LOG', COUNT(*) FROM DETECTION_LOG;
```

### Query 2: Cryptojacking & Rogue Process Detection (Security Audit)
```sql
SELECT 
    r.run_id,
    a.algo_name,
    d.name AS developer_name,
    d.team,
    cn.hostname,
    f.ipc_ratio,
    f.cache_miss_rate,
    dl.similarity_score,
    dl.alert_level,
    dl.classification_result
FROM DETECTION_LOG dl
JOIN BASELINE_PATTERN bp ON dl.baseline_id = bp.baseline_id
JOIN FINGERPRINT f ON dl.fingerprint_id = f.fingerprint_id
JOIN EXECUTION_RUN r ON f.run_id = r.run_id
JOIN ALGORITHM a ON r.algo_id = a.algo_id
JOIN DEVELOPER d ON a.dev_id = d.dev_id
JOIN COMPUTE_NODE cn ON r.node_id = cn.node_id
WHERE dl.alert_level = 'Critical'
  AND dl.classification_result = 'Malicious_Cryptojacking'
ORDER BY dl.similarity_score DESC
LIMIT 10;
```

### Query 3: HPC vs Security Workload Counter Clustering
```sql
SELECT 
    bp.category,
    bp.pattern_name,
    COUNT(f.fingerprint_id) AS total_evaluated_runs,
    ROUND(AVG(f.ipc_ratio), 3) AS observed_avg_ipc,
    ROUND(AVG(f.cache_miss_rate), 2) AS observed_avg_cache_miss_pct,
    ROUND(AVG(f.branch_misprediction_rate), 2) AS observed_avg_branch_mispred_pct,
    ROUND(AVG(dl.similarity_score), 2) AS avg_congruence_score
FROM DETECTION_LOG dl
JOIN BASELINE_PATTERN bp ON dl.baseline_id = bp.baseline_id
JOIN FINGERPRINT f ON dl.fingerprint_id = f.fingerprint_id
GROUP BY bp.baseline_id, bp.category, bp.pattern_name
HAVING total_evaluated_runs > 20
ORDER BY observed_avg_ipc DESC;
```

### Query 4: Cross-Architecture Performance Breakdown (x86_64 vs ARM64)
```sql
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
```
