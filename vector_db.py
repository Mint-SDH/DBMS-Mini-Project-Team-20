#!/usr/bin/env python3
"""
=============================================================================
VECTOR DATABASE ENGINE FOR HARDWARE TELEMETRY & THREAT PROFILING
DBMS Mini Project | Algorithmic Execution Fingerprinting
PES University - Group 20
=============================================================================
This module implements a Vector Database for multidimensional execution
fingerprints. It provides:
  1. Multidimensional Vectorization of hardware telemetry:
     [ipc_ratio, cache_miss_rate, branch_misprediction_rate, peak_memory_mb, duration_s]
  2. Cosine Similarity & Euclidean L2 Distance metric spaces.
  3. k-Nearest Neighbors (k-NN) vector index for zero-day & anomaly similarity search.
  4. Full RUD Operations (Read/Search, Update vector, Delete vector).
  5. Persistence to disk (vector_store.json).
=============================================================================
"""

import os
import json
import math
import numpy as np
import pymysql

VECTOR_STORE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_store.json")

class VectorDB:
    def __init__(self, filepath=VECTOR_STORE_PATH):
        self.filepath = filepath
        self.vectors = {}  # id -> {"vector": [...], "metadata": {...}}
        self.load()

    def normalize(self, vec):
        """Min-Max or L2 normalization for telemetry vector dimensions."""
        # Telemetry bounds for normalization:
        # IPC: [0.0, 4.0], Cache Miss: [0.0, 100.0], Branch Mispred: [0.0, 50.0], Peak Mem: [0.0, 32768.0], Duration: [0.0, 3600.0]
        bounds = [(0.0, 4.0), (0.0, 100.0), (0.0, 50.0), (0.0, 32768.0), (0.0, 3600.0)]
        norm = []
        for i, val in enumerate(vec):
            min_v, max_v = bounds[i] if i < len(bounds) else (0.0, 1.0)
            clamped = max(min_v, min(max_v, float(val)))
            norm.append((clamped - min_v) / (max_v - min_v + 1e-9))
        return norm

    def cosine_similarity(self, v1, v2):
        a = np.array(v1, dtype=float)
        b = np.array(v2, dtype=float)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    def euclidean_distance(self, v1, v2):
        a = np.array(v1, dtype=float)
        b = np.array(v2, dtype=float)
        return float(np.linalg.norm(a - b))

    def insert(self, vector_id, raw_vector, metadata):
        """Create / Insert a vector with metadata."""
        norm_vec = self.normalize(raw_vector)
        self.vectors[str(vector_id)] = {
            "raw_vector": [round(float(x), 4) for x in raw_vector],
            "norm_vector": [round(float(x), 6) for x in norm_vec],
            "metadata": metadata
        }

    def get(self, vector_id):
        """Read a single vector by ID."""
        return self.vectors.get(str(vector_id))

    def update(self, vector_id, raw_vector=None, metadata=None):
        """Update an existing vector or its metadata (U in RUD)."""
        vid = str(vector_id)
        if vid not in self.vectors:
            return False
        if raw_vector is not None:
            self.vectors[vid]["raw_vector"] = [round(float(x), 4) for x in raw_vector]
            self.vectors[vid]["norm_vector"] = [round(float(x), 6) for x in self.normalize(raw_vector)]
        if metadata is not None:
            self.vectors[vid]["metadata"].update(metadata)
        self.save()
        return True

    def delete(self, vector_id):
        """Delete a vector from index (D in RUD)."""
        vid = str(vector_id)
        if vid in self.vectors:
            del self.vectors[vid]
            self.save()
            return True
        return False

    def search_knn(self, query_raw_vector, top_k=5, metric="cosine"):
        """
        Query / Read Top-K nearest neighbors (R in RUD).
        Returns matching records ranked by similarity.
        """
        norm_query = self.normalize(query_raw_vector)
        results = []

        for vid, entry in self.vectors.items():
            candidate = entry["norm_vector"]
            if metric == "cosine":
                score = self.cosine_similarity(norm_query, candidate)
                sim_pct = round(score * 100, 2)
            else:
                dist = self.euclidean_distance(norm_query, candidate)
                score = 1.0 / (1.0 + dist)
                sim_pct = round(score * 100, 2)

            results.append({
                "vector_id": vid,
                "similarity_score": sim_pct,
                "distance": round(self.euclidean_distance(norm_query, candidate), 4),
                "raw_vector": entry["raw_vector"],
                "metadata": entry["metadata"]
            })

        # Sort descending by similarity score
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    def save(self):
        """Persist vector index to JSON."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.vectors, f, indent=2)

    def load(self):
        """Load vector index from JSON if exists."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.vectors = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load vector store ({e}). Starting fresh.")
                self.vectors = {}

    def populate_from_mysql(self, mysql_host="localhost", mysql_user="root", mysql_password="Mint@123", db_name="algo_fingerprint_db", limit=1500):
        """Bootstrap the vector store from MySQL fingerprints and baseline patterns."""
        print(f"Ingesting vector embeddings from MySQL '{db_name}'...")
        conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=db_name)
        with conn.cursor() as cur:
            # 1. Ingest Golden Baseline Vectors
            cur.execute("""
                SELECT baseline_id, pattern_name, category, expected_ipc, expected_cache_miss_rate 
                FROM baseline_pattern;
            """)
            baselines = cur.fetchall()
            for row in baselines:
                b_id, p_name, cat, exp_ipc, exp_cm = row
                # Vector: [IPC, Cache Miss %, Branch Mispred % (est. 2.0), Peak Mem (est. 1024), Duration (est. 60)]
                raw_vec = [float(exp_ipc), float(exp_cm), 2.5, 1024.0, 60.0]
                self.insert(
                    vector_id=f"BASELINE_{b_id}",
                    raw_vector=raw_vec,
                    metadata={
                        "type": "Golden_Baseline",
                        "baseline_id": b_id,
                        "name": p_name,
                        "category": cat,
                        "description": f"Golden reference vector for {p_name}"
                    }
                )

            # 2. Ingest Fingerprint Telemetry Vectors
            cur.execute(f"""
                SELECT 
                    f.fingerprint_id,
                    f.run_id,
                    a.algo_name,
                    d.name AS dev_name,
                    d.team,
                    cn.hostname,
                    f.ipc_ratio,
                    f.cache_miss_rate,
                    f.branch_misprediction_rate,
                    r.peak_memory_mb,
                    TIMESTAMPDIFF(SECOND, r.start_time, COALESCE(r.end_time, DATE_ADD(r.start_time, INTERVAL 60 SECOND))) AS duration_s,
                    dl.alert_level,
                    dl.classification_result
                FROM fingerprint f
                JOIN execution_run r ON f.run_id = r.run_id
                JOIN algorithm a ON r.algo_id = a.algo_id
                JOIN developer d ON a.dev_id = d.dev_id
                JOIN compute_node cn ON r.node_id = cn.node_id
                LEFT JOIN detection_log dl ON f.fingerprint_id = dl.fingerprint_id
                LIMIT {limit};
            """)
            rows = cur.fetchall()
            for r in rows:
                f_id, r_id, a_name, dev_name, team, hostname, ipc, cm, bm, mem, dur, alert, classification = r
                raw_vec = [
                    float(ipc),
                    float(cm),
                    float(bm),
                    float(mem if mem is not None else 512.0),
                    float(dur if dur is not None else 30.0)
                ]
                self.insert(
                    vector_id=f"FP_{f_id}",
                    raw_vector=raw_vec,
                    metadata={
                        "type": "Runtime_Fingerprint",
                        "fingerprint_id": f_id,
                        "run_id": r_id,
                        "algo_name": a_name,
                        "developer": dev_name,
                        "team": team,
                        "hostname": hostname,
                        "alert_level": alert or "Info",
                        "classification": classification or "Verified_Safe"
                    }
                )
        conn.close()
        self.save()
        print(f"Successfully vectorized and indexed {len(self.vectors)} hardware telemetry vectors!")

if __name__ == "__main__":
    vdb = VectorDB()
    vdb.populate_from_mysql()
    
    # Test k-NN search with an anomalous cryptojacking-like telemetry vector
    # Low IPC (0.6), high cache miss (38.0%), high branch mispred (16.0%), 4096 MB peak mem, 120s duration
    print("\n--- Testing k-NN Anomaly Vector Search ---")
    query_vector = [0.62, 36.5, 15.2, 4096.0, 120.0]
    print("Query Vector:", query_vector)
    matches = vdb.search_knn(query_vector, top_k=3)
    for idx, match in enumerate(matches, 1):
        print(f"{idx}. [{match['similarity_score']}% Match] ID: {match['vector_id']}, Type: {match['metadata']['type']}, Class: {match['metadata'].get('classification') or match['metadata'].get('category')}")

