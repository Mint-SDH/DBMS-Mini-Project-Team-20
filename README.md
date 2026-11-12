# Algorithmic Execution Fingerprinting & Threat Profiler

**Course:** UE23CS351A / UE24CS351A – Database Management Systems  
**Department of Computer Science & Engineering | PES University, Bengaluru**  
**Academic Semester:** AUG – DEC 2026 (5th Semester)  
**Team (Group 20):**  
- **Sanyam Deven Hiran** (PES2UG24CS446)  
- **Shashank A** (PES2UG24CS461)  
**Faculty Guide:** Dr. Shilpa S, Assistant Professor  

---

## 📌 Project Overview & Architecture

**ExecutionGuard** is a multi-model database security platform that tracks low-level CPU Hardware Performance Counters (HPCs)—including **Instructions Per Cycle (IPC)**, **Cache Miss Rates**, **Branch Mispredictions**, and **Memory Footprints**—to detect zero-day cryptojacking malware and rogue processes.

The system combines:
1. **Relational Core (MySQL 8.0+)**: Strongly-typed relational schema across 7 entities, 1:1 run-to-fingerprint cardinality, automated threat mitigation triggers, stored procedures, deterministic functions, and recursive CTEs for tracking polymorphic algorithm lineages.
2. **NoSQL Graph Database (Neo4j & Cypher)**: Graph-native relationship storage to compute 1-to-3 hop lateral threat blast radii and node quarantine status.
3. **Multidimensional Vector Database**: 5D normalized metric space ($\vec{v} = [IPC, CacheMiss, BranchMispred, PeakMem, Duration]$) executing sub-millisecond Cosine Similarity and k-NN retrieval for zero-day malware detection against golden baselines.
4. **Next.js Fullstack Dashboard**: Real-time interactive UI with role-based access control (`sec_admin` vs `sec_analyst`), live SQL query runner, vector sliders, and graph visualizer.

---

### 👥 Team Division of Work

In accordance with course requirements, the project was designed, implemented, and integrated collaboratively:

#### 👤 Sanyam Deven Hiran (PES2UG24CS446)
- **Domain Problem Formulation & Mathematical Modeling:** Hardware counter metric distributions across 5 architectural archetypes.
- **Entity-Relationship (ER) & Relational Schema Mapping:** 7-entity ER model and relational schema mapping (`docs/architecture/er_diagram.png`, `docs/architecture/schema_diagram.png`).
- **Core MySQL DDL & Relational Constraints:** DDL table definitions with strict 1:1 run-to-fingerprint cardinality and database-level RBAC (`database/schema/schema_ddl.sql`, `database/schema/truncate_tables.sql`).
- **Advanced Stored Procedures, Functions & Triggers:** Stored procedure `GetRunFingerprintProfile`, deterministic function `CalculateIPCDeviation`, validation triggers, threat auto-mitigation triggers, and security view `vw_critical_security_anomalies` (`database/schema/procedures_and_triggers.sql`).
- **Multidimensional Vector Database Engine:** 5D continuous telemetry metric space with Cosine Similarity and k-NN retrieval (`backend/vector_db.py`, `backend/vector_store.json`).
- **Backend REST API Framework:** FastAPI backend core endpoints and RBAC authentication gating (`backend/api_server.py`).

#### 👤 Shashank A (PES2UG24CS461)
- **Synthetic Telemetry Ingestion Pipeline:** High-throughput data generation engine using Faker and NumPy modeling 5 realistic microarchitectural archetypes (`backend/generate_synthetic_data.py`).
- **Database Loaders & Ingestion Tooling:** Batched transactional SQL inserter (`backend/insert_to_db.py`, `database/seed_data/algo_fingerprint_data.sql`), high-speed `LOAD DATA INFILE` pipeline (`database/seed_data/load_csv.sql`), and schema reset/populate workflow (`backend/reset_and_populate.py`, `database/seed_data/DATASET_GUIDE.md`).
- **Relational Analytical SQL Suite:** Formulated complex multi-table joins, correlated subqueries, nested queries, ACID transactions, and recursive CTEs for polymorphic algorithm mutation tracking (`database/queries/analytical_queries.sql`).
- **NoSQL Graph Database Integration:** Neo4j Cypher engine with in-memory graph fallback, lateral infection pathways, multi-hop threat blast-radius traversals, and node quarantine (`backend/graph_db.py`, API graph endpoints in `backend/api_server.py`).
- **Fullstack Next.js Frontend Dashboard:** Modern interactive dashboard using Next.js 16 (App Router), TypeScript, and Tailwind CSS with live telemetry metrics, threat monitor, interactive query runner, and vector similarity explorer (`frontend/`).

---

## 🏗️ Repository Structure

```text
DBMS-Mini-Project/
├── backend/                        # High-performance Python backend & multi-model engines
│   ├── api_server.py               # FastAPI REST service connecting MySQL, Graph & Vector
│   ├── vector_db.py                # 5D Vector database engine & k-NN cosine similarity
│   ├── graph_db.py                 # Neo4j Cypher graph engine & threat blast radius
│   ├── generate_synthetic_data.py  # Faker & NumPy telemetry dataset generator
│   ├── reset_and_populate.py       # Automated schema reset and topological data population
│   ├── insert_to_db.py             # Transactional batch SQL loader
│   └── vector_store.json           # Seeded vector embeddings database
│
├── database/                       # Relational schema, seed data, and analytical queries
│   ├── schema/                     # DDL table specifications, procedures, views, and triggers
│   │   ├── schema_ddl.sql          # Core table definitions, constraints, and RBAC roles
│   │   ├── procedures_and_triggers.sql # Stored procedures, functions, and audit triggers
│   │   └── truncate_tables.sql     # Safe table truncation utility
│   ├── queries/                    # Advanced relational queries and query evaluation
│   │   └── analytical_queries.sql  # Multi-table joins, subqueries, ACID tests, and recursive CTEs
│   └── seed_data/                  # Seed dataset artifacts and bulk loading scripts
│       ├── algo_fingerprint_data.sql # Seed SQL script (17,000+ batched insert statements)
│       ├── load_csv.sql            # High-speed LOAD DATA LOCAL INFILE script
│       ├── DATASET_GUIDE.md        # Comprehensive synthetic dataset & archetype guide
│       └── csv_data/               # Raw generated CSV tables
│
├── frontend/                       # Next.js 16 fullstack cybersecurity dashboard
│   ├── app/                        # Next.js App Router components, layout, and views
│   ├── public/                     # Static UI assets
│   ├── package.json
│   └── tsconfig.json
│
└── docs/                           # Architecture diagrams and system design specifications
    └── architecture/
        ├── er_diagram.png          # 7-entity Crow's foot ER diagram
        ├── schema_diagram.png      # Relational schema mapping with foreign key dependencies
        └── pes_logo.png            # PES University academic emblem
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **Node.js v18+ & npm**
- **MySQL 8.0+** running on `localhost:3306`

### 2. Database Setup (MySQL 8.0+)
Open your MySQL terminal and execute:
```sql
SOURCE database/schema/schema_ddl.sql;
SOURCE database/schema/procedures_and_triggers.sql;
```

To populate the complete dataset:
```powershell
python backend/reset_and_populate.py
```
*(Alternatively, use `python backend/insert_to_db.py` to ingest the SQL seed dump directly)*

### 3. Start Backend API Service
```powershell
cd backend
python api_server.py
```
- API live at: `http://localhost:8000`
- Interactive Swagger docs: `http://localhost:8000/docs`

### 4. Start Next.js Frontend Dashboard
In a separate terminal:
```powershell
cd frontend
npm run dev
```
- Open browser at: `http://localhost:3000`

### 5. Execute Analytical SQL Queries
```powershell
# Open MySQL client and execute the analytical query suite:
mysql -u root -p algo_fingerprint_db < database/queries/analytical_queries.sql
```
