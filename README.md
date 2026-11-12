# Algorithmic Execution Fingerprinting & Threat Profiler

**Course:** UE23CS351A / UE24CS351A – Database Management Systems  
**Department of Computer Science & Engineering | PES University, Bengaluru**  
**Academic Semester:** AUG – DEC 2026 (5th Semester)  
**Team (Group 20):**  
- **Sanyam Deven Hiran** (PES2UG24CS446) — *Lead Contributor (This Repository)*  
- **Shashank A** (PES2UG24CS461) — *Teammate (Data Generation, Graph DB, Frontend)*  
**Faculty Guide:** Dr. Shilpa S, Assistant Professor  

---

## 📌 Project Overview & Team Division of Work

This project implements a multi-model database security platform tracking low-level CPU Hardware Performance Counters (HPCs)—including **Instructions Per Cycle (IPC)**, **Cache Miss Rates**, **Branch Mispredictions**, and **Memory Footprints**—to detect zero-day cryptojacking malware and rogue processes.

In accordance with the 2-member project distribution requirements, the implementation is partitioned into two halves:

### 👤 Part A: Sanyam Deven Hiran (PES2UG24CS446) — [Pushed to this Repository]
1. **Domain Problem Formulation & Mathematical Modeling:** Hardware counter metric distributions across 5 architectural archetypes.
2. **Entity-Relationship (ER) & Relational Schema Mapping:**
   - [`report_assets/er_diagram.png`](report_assets/er_diagram.png): 7-entity ER model with $1:1$, $1:N$, and $M:N$ cardinalities.
   - [`report_assets/schema_diagram.png`](report_assets/schema_diagram.png): Complete relational schema mapping with foreign key dependencies.
3. **Core MySQL DDL & Relational Constraints:**
   - [`schema_ddl.sql`](schema_ddl.sql): Complete DDL table definitions with primary keys, cascading foreign keys, and strict **1:1** cardinality (`FINGERPRINT.run_id UNIQUE`).
   - Database-level Role-Based Access Control (`sec_admin` and `sec_analyst`).
   - [`truncate_tables.sql`](truncate_tables.sql): Clean schema reset utility.
4. **Advanced Stored Procedures, Functions & Automated Triggers:**
   - [`procedures_and_triggers.sql`](procedures_and_triggers.sql):
     - Stored Procedure `GetRunFingerprintProfile(p_run_id)`
     - Stored Deterministic Function `CalculateIPCDeviation(p_fingerprint_id)`
     - Trigger `trg_validate_fingerprint_bounds` (BEFORE INSERT on `FINGERPRINT`)
     - Trigger `trg_auto_terminate_critical_threat` (AFTER INSERT on `DETECTION_LOG` for automated threat mitigation)
     - Relational Security Audit View `vw_critical_security_anomalies`
5. **Multidimensional Vector Database Engine:**
   - [`vector_db.py`](vector_db.py) & [`vector_store.json`](vector_store.json): 5D continuous telemetry metric space ($\vec{v} = [IPC, CacheMiss, BranchMispred, PeakMem, Duration]$) utilizing **Cosine Similarity** and **k-NN retrieval** for zero-day malware detection against golden baselines with complete Vector RUD (Read/Search, Update, Delete).
6. **Backend REST API Service:**
   - [`api_server.py`](api_server.py): FastAPI backend providing relational query execution, RBAC authentication gating, and vector similarity search.
7. **Official Academic Documentation & PDF Compiler:**
   - [`generate_final_report_pdf.py`](generate_final_report_pdf.py): ReportLab PDF generation script.
   - [`PES2UG24CS446_PES2UG24CS461_Final_Report.pdf`](PES2UG24CS446_PES2UG24CS461_Final_Report.pdf): 17-page formal PES University academic report.
   - [`REPORT.md`](REPORT.md): Comprehensive Markdown documentation covering all 16 chapters.

---

### 👤 Part B: Shashank A (PES2UG24CS461) — [To be Merged by Teammate]
1. **Synthetic Telemetry Ingestion Pipeline:** Faker & NumPy data generator (`generate_synthetic_data.py`), database population scripts (`reset_and_populate.py`, `insert_to_db.py`, `load_csv.sql`), and raw CSV tables (`csv_data/`).
2. **NoSQL Graph Database Integration:** Neo4j Cypher engine (`graph_db.py`), lateral infection pathways, and multi-hop threat blast-radius traversals.
3. **Frontend User Interface:** Modern Next.js application (`frontend/`) with Tailwind CSS, telemetry dashboards, interactive vector sliders, and query runner.
4. **Relational Analytical Queries:** Complex multi-table joins, correlated subqueries, and recursive CTE tests.

---

## 🚀 How to Run Sanyam's Modules

### 1. Database Setup (MySQL 8.0+)
```sql
SOURCE schema_ddl.sql;
SOURCE procedures_and_triggers.sql;
```

### 2. Vector Database k-NN Anomaly Matcher
```powershell
python vector_db.py
```

### 3. FastAPI Backend Service
```powershell
python api_server.py
```
*Live at:* `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`)

### 4. Compile Academic Report PDF
```powershell
python generate_final_report_pdf.py
```
Outputs the official PES University report: `PES2UG24CS446_PES2UG24CS461_Final_Report.pdf`.
