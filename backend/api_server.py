#!/usr/bin/env python3
"""
=============================================================================
FASTAPI BACKEND SERVICE & DATABASE INTEGRATION ENGINE
DBMS Mini Project | Algorithmic Execution Fingerprinting
PES University - Group 20
=============================================================================
"""

import os
import sys
import time
import json
import pymysql
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from vector_db import VectorDB

try:
    from graph_db import ThreatGraphDB
    GRAPH_MODULE_PRESENT = True
except ImportError:
    GRAPH_MODULE_PRESENT = False
    ThreatGraphDB = None

app = FastAPI(
    title="Algorithmic Execution Fingerprinting API",
    version="1.0.0",
    description="Backend API integrating MySQL Relational DB, Neo4j Graph DB, and Vector Database."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASS = os.getenv("MYSQL_PASS", "Marty@66")
MYSQL_DB = os.getenv("MYSQL_DB", "algo_fingerprint_db")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

# Initialize Subsystems
vector_db = VectorDB()
if len(vector_db.vectors) == 0:
    try:
        vector_db.populate_from_mysql(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
    except Exception as e:
        print(f"Warning: Could not populate Vector DB ({e})")

threat_graph = None
if GRAPH_MODULE_PRESENT and ThreatGraphDB is not None:
    try:
        threat_graph = ThreatGraphDB()
        threat_graph.sync_from_mysql(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
    except Exception as e:
        print(f"Warning: Could not populate Graph DB ({e})")


def get_db_connection(user=MYSQL_USER, password=MYSQL_PASS):
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=user,
        password=password,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )


# --- Request Models ---

class LoginRequest(BaseModel):
    username: str
    password: str
    role: str  # "sec_admin" or "sec_analyst"

class VectorSearchRequest(BaseModel):
    ipc_ratio: float
    cache_miss_rate: float
    branch_misprediction_rate: float
    peak_memory_mb: float = 1024.0
    duration_s: float = 60.0
    top_k: int = 5

class VectorUpdateRequest(BaseModel):
    vector_id: str
    ipc_ratio: Optional[float] = None
    cache_miss_rate: Optional[float] = None
    branch_misprediction_rate: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class QuarantineRequest(BaseModel):
    node_id: int
    reason: str = "Automated threat response"

class SQLQueryRequest(BaseModel):
    query: str
    role: str = "sec_analyst"


# --- API Routes ---

@app.get("/api/health")
def health_check():
    mysql_ok = False
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        conn.close()
        mysql_ok = True
    except Exception:
        mysql_ok = False

    return {
        "status": "healthy",
        "mysql_connected": mysql_ok,
        "graph_nodes": len(threat_graph.fallback.nodes) if threat_graph else 0,
        "graph_edges": sum(len(v) for v in threat_graph.fallback.edges.values()) if threat_graph else 0,
        "vector_index_size": len(vector_db.vectors),
        "timestamp": time.time()
    }


@app.post("/api/auth/login")
def login(creds: LoginRequest):
    # Simulated auth matching DB RBAC users
    valid_users = {
        "admin": {"password": "Admin@Sec2026!", "role": "sec_admin", "name": "SecOps Administrator", "permissions": ["ALL"]},
        "analyst": {"password": "Analyst@Sec2026!", "role": "sec_analyst", "name": "Security Analyst", "permissions": ["SELECT", "INSERT", "EXECUTE"]}
    }

    user_info = valid_users.get(creds.username.lower())
    if not user_info or (creds.password != user_info["password"] and creds.password != "password"):
        # Allow default convenient login for demonstration
        if creds.username.lower() in ("admin", "analyst"):
            role = "sec_admin" if creds.username.lower() == "admin" else "sec_analyst"
            return {
                "token": f"mock-jwt-token-{creds.username}",
                "user": {
                    "username": creds.username,
                    "name": "SecOps Administrator" if role == "sec_admin" else "Security Analyst",
                    "role": role,
                    "db_user": "admin_user" if role == "sec_admin" else "analyst_user"
                }
            }
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "token": f"mock-jwt-token-{creds.username}",
        "user": {
            "username": creds.username,
            "name": user_info["name"],
            "role": user_info["role"],
            "db_user": "admin_user" if user_info["role"] == "sec_admin" else "analyst_user"
        }
    }


@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total_runs FROM execution_run;")
            total_runs = cur.fetchone()["total_runs"]

            cur.execute("SELECT COUNT(*) AS total_fingerprints FROM fingerprint;")
            total_fingerprints = cur.fetchone()["total_fingerprints"]

            cur.execute("SELECT COUNT(*) AS total_algorithms FROM algorithm;")
            total_algorithms = cur.fetchone()["total_algorithms"]

            cur.execute("SELECT COUNT(*) AS total_nodes FROM compute_node;")
            total_nodes = cur.fetchone()["total_nodes"]

            cur.execute("SELECT COUNT(*) AS critical_threats FROM detection_log WHERE alert_level = 'Critical';")
            critical_threats = cur.fetchone()["critical_threats"]

            cur.execute("SELECT COUNT(*) AS high_threats FROM detection_log WHERE alert_level = 'High';")
            high_threats = cur.fetchone()["high_threats"]

            cur.execute("""
                SELECT alert_level, COUNT(*) AS count 
                FROM detection_log 
                GROUP BY alert_level;
            """)
            alert_dist = cur.fetchall()

            cur.execute("""
                SELECT cn.cpu_architecture, COUNT(DISTINCT r.run_id) AS runs, ROUND(AVG(f.ipc_ratio), 2) AS avg_ipc
                FROM compute_node cn
                JOIN execution_run r ON cn.node_id = r.node_id
                JOIN fingerprint f ON r.run_id = f.run_id
                GROUP BY cn.cpu_architecture;
            """)
            arch_dist = cur.fetchall()

            return {
                "total_runs": total_runs,
                "total_fingerprints": total_fingerprints,
                "total_algorithms": total_algorithms,
                "total_nodes": total_nodes,
                "critical_threats": critical_threats,
                "high_threats": high_threats,
                "alert_distribution": alert_dist,
                "architecture_distribution": arch_dist,
                "vector_db_size": len(vector_db.vectors),
                "graph_entities": len(threat_graph.fallback.nodes) if threat_graph else 0
            }
    finally:
        conn.close()


@app.get("/api/anomalies/critical")
def get_critical_anomalies(limit: int = 25, offset: int = 0):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT 
                    dl.detection_id, er.run_id, er.node_id, a.algo_name, d.name AS developer_name, d.team,
                    cn.hostname, bp.pattern_name AS detected_threat_signature, dl.similarity_score,
                    dl.alert_level, dl.classification_result, fp.signature_hash,
                    fp.ipc_ratio, fp.cache_miss_rate, fp.branch_misprediction_rate, er.peak_memory_mb
                FROM detection_log dl
                JOIN baseline_pattern bp ON dl.baseline_id = bp.baseline_id
                JOIN fingerprint fp ON dl.fingerprint_id = fp.fingerprint_id
                JOIN execution_run er ON fp.run_id = er.run_id
                JOIN algorithm a ON er.algo_id = a.algo_id
                JOIN developer d ON a.dev_id = d.dev_id
                JOIN compute_node cn ON er.node_id = cn.node_id
                WHERE dl.alert_level IN ('Critical', 'High')
                ORDER BY dl.similarity_score DESC
                LIMIT {limit} OFFSET {offset};
            """)
            records = cur.fetchall()
            return {"count": len(records), "data": records}
    finally:
        conn.close()


@app.get("/api/queries/advanced")
def get_advanced_query_samples():
    """Returns curated results of the required academic queries."""
    conn = get_db_connection()
    results = {}
    try:
        with conn.cursor() as cur:
            # 1. Recursive CTE
            cur.execute("""
                WITH RECURSIVE AlgoLineage AS (
                    SELECT 
                        algo_id, algo_name, version, parent_algo_id, 1 AS lineage_depth, 
                        CAST(algo_name AS CHAR(500)) AS lineage_path
                    FROM algorithm
                    WHERE parent_algo_id IS NULL AND algo_id IN (2, 4, 6, 14)
                    
                    UNION ALL
                    
                    SELECT 
                        a.algo_id, a.algo_name, a.version, a.parent_algo_id, al.lineage_depth + 1, 
                        CONCAT(al.lineage_path, ' -> ', a.algo_name)
                    FROM algorithm a
                    JOIN AlgoLineage al ON a.parent_algo_id = al.algo_id
                    WHERE al.lineage_depth < 10
                )
                SELECT algo_id, lineage_depth, lineage_path FROM AlgoLineage ORDER BY lineage_path LIMIT 12;
            """)
            results["recursive_cte"] = cur.fetchall()

            # 2. Correlated Subquery: Runs consuming above-average peak memory for their programming language
            cur.execute("""
                SELECT 
                    a1.algo_id, a1.algo_name, a1.language, er1.run_id, er1.peak_memory_mb
                FROM algorithm a1
                JOIN execution_run er1 ON a1.algo_id = er1.algo_id
                WHERE er1.peak_memory_mb > (
                    SELECT AVG(er2.peak_memory_mb)
                    FROM algorithm a2
                    JOIN execution_run er2 ON a2.algo_id = er2.algo_id
                    WHERE a2.language = a1.language
                )
                LIMIT 8;
            """)
            results["correlated_subquery"] = cur.fetchall()

            # 3. CTE Non-Recursive: Team-level security risk ranking
            cur.execute("""
                WITH TeamThreatScore AS (
                    SELECT 
                        d.team,
                        COUNT(DISTINCT r.run_id) AS total_team_runs,
                        SUM(CASE WHEN dl.alert_level = 'Critical' THEN 1 ELSE 0 END) AS critical_count,
                        ROUND(AVG(dl.similarity_score), 2) AS mean_similarity
                    FROM developer d
                    JOIN algorithm a ON d.dev_id = a.dev_id
                    JOIN execution_run r ON a.algo_id = r.algo_id
                    JOIN fingerprint f ON r.run_id = f.run_id
                    JOIN detection_log dl ON f.fingerprint_id = dl.fingerprint_id
                    GROUP BY d.team
                )
                SELECT 
                    team, total_team_runs, critical_count, mean_similarity,
                    ROUND((critical_count / total_team_runs) * 100, 2) AS threat_density_pct
                FROM TeamThreatScore
                ORDER BY critical_count DESC;
            """)
            results["cte_risk_scoring"] = cur.fetchall()

            # 4. Multi-table JOIN with Aggregation
            cur.execute("""
                SELECT 
                    cn.cpu_architecture,
                    COUNT(er.run_id) AS total_executions,
                    ROUND(SUM(er.peak_memory_mb), 2) AS total_memory_allocated_mb,
                    ROUND(AVG(fp.ipc_ratio), 3) AS average_ipc_ratio
                FROM compute_node cn
                JOIN execution_run er ON cn.node_id = er.node_id
                JOIN fingerprint fp ON er.run_id = fp.run_id
                GROUP BY cn.cpu_architecture
                ORDER BY total_memory_allocated_mb DESC;
            """)
            results["multitable_join"] = cur.fetchall()

            # 5. Stored Function call CalculateIPCDeviation
            cur.execute("""
                SELECT 
                    f.fingerprint_id,
                    f.ipc_ratio,
                    CalculateIPCDeviation(f.fingerprint_id) AS deviation_score_pct
                FROM fingerprint f
                LIMIT 5;
            """)
            results["stored_function_calls"] = cur.fetchall()

        return results
    finally:
        conn.close()


@app.post("/api/queries/run")
def execute_custom_sql(req: SQLQueryRequest):
    """Executes arbitrary SQL queries with role gating."""
    clean_query = req.query.strip()
    upper = clean_query.upper()

    # RBAC Enforcement: sec_analyst cannot run DROP, ALTER, TRUNCATE, DELETE without where, etc.
    if req.role == "sec_analyst":
        forbidden = ["DROP", "ALTER", "TRUNCATE", "GRANT", "REVOKE", "CREATE USER"]
        if any(upper.startswith(w) or f" {w} " in upper for w in forbidden):
            raise HTTPException(
                status_code=403, 
                detail="Access Denied: Role 'sec_analyst' does not possess DDL or user management permissions. Switch to 'sec_admin' role."
            )

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(clean_query)
            if upper.startswith("SELECT") or upper.startswith("WITH") or upper.startswith("SHOW") or upper.startswith("DESC"):
                rows = cur.fetchall()
                return {"type": "SELECT", "rows": rows, "count": len(rows)}
            else:
                conn.commit()
                return {"type": "MUTATION", "affected_rows": cur.rowcount, "message": "Statement executed successfully."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


# --- Neo4j Graph Routes ---

@app.get("/api/graph/blast-radius")
def get_graph_blast_radius(entity_id: str = "ALGO_2", depth: int = 2):
    """Computes lateral threat blast radius across the graph database."""
    if not threat_graph:
        return {"nodes": [], "edges": [], "summary": "Graph module pending teammate integration"}
    res = threat_graph.read_blast_radius(entity_id, max_depth=depth)
    return res


@app.post("/api/graph/quarantine")
def quarantine_node(req: QuarantineRequest):
    """Graph U: Quarantines a compute node in graph and marks it isolated."""
    if not threat_graph:
        return {"message": "Graph module pending teammate integration"}
    nid = f"NODE_{req.node_id}"
    res = threat_graph.update_node_status(nid, "QUARANTINED")
    return {"message": f"Compute node {nid} successfully quarantined.", "details": res}


@app.delete("/api/graph/edge")
def delete_graph_edge(src: str, dst: str):
    """Graph D: Severs an edge relationship."""
    if not threat_graph:
        return {"message": "Graph module pending teammate integration"}
    res = threat_graph.delete_edge_link(src, dst)
    return {"message": "Graph edge severed.", "result": res}


# --- Vector Database Routes ---

@app.post("/api/vector/search")
def search_vector_similarity(req: VectorSearchRequest):
    """Vector R: k-NN similarity search across hardware performance vectors."""
    query_raw = [
        req.ipc_ratio,
        req.cache_miss_rate,
        req.branch_misprediction_rate,
        req.peak_memory_mb,
        req.duration_s
    ]
    matches = vector_db.search_knn(query_raw, top_k=req.top_k)
    return {
        "query_vector": query_raw,
        "results_count": len(matches),
        "matches": matches
    }


@app.post("/api/vector/update")
def update_vector_embedding(req: VectorUpdateRequest):
    """Vector U: Updates vector embedding."""
    curr = vector_db.get(req.vector_id)
    if not curr:
        raise HTTPException(status_code=404, detail="Vector ID not found")
    
    new_raw = curr["raw_vector"]
    if req.ipc_ratio is not None:
        new_raw[0] = req.ipc_ratio
    if req.cache_miss_rate is not None:
        new_raw[1] = req.cache_miss_rate
    if req.branch_misprediction_rate is not None:
        new_raw[2] = req.branch_misprediction_rate

    vector_db.update(req.vector_id, raw_vector=new_raw, metadata=req.metadata)
    return {"status": "Success", "updated_vector": vector_db.get(req.vector_id)}


@app.delete("/api/vector/delete")
def delete_vector_entry(vector_id: str = Query(...)):
    """Vector D: Deletes vector from index."""
    success = vector_db.delete(vector_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vector ID not found")
    return {"status": "Success", "deleted_vector_id": vector_id}


if __name__ == "__main__":
    import uvicorn
    print("Starting API Server on http://localhost:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

