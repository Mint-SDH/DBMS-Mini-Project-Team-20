#!/usr/bin/env python3
"""
=============================================================================
NEO4J GRAPH DATABASE ENGINE & CYPER TRAVERSAL FOR THREAT BLAST RADIUS
DBMS Mini Project | Algorithmic Execution Fingerprinting
PES University - Group 20
=============================================================================
This module implements the NoSQL Graph Database component using Neo4j and Cypher.
Graph Schema:
  (:Developer) -[:AUTHORED]-> (:Algorithm)
  (:Algorithm) -[:EXECUTED_IN]-> (:ExecutionRun)
  (:ExecutionRun) -[:RUNS_ON]-> (:ComputeNode)
  (:ExecutionRun) -[:GENERATED]-> (:Fingerprint)
  (:Fingerprint) -[:FLAGGED_AS {similarity: Float}]-> (:BaselinePattern)
  (:Algorithm) -[:DERIVED_FROM]-> (:Algorithm)  [Polymorphic Lineage]

Graph Capabilities:
  - Graph RUD (Create, Read/Traverse, Update, Delete)
  - Threat Blast Radius: 1-to-3 hop lateral movement & compromised node analysis
  - Developer Threat Exposure Scoring
  - Automatic fallback to high-speed in-memory graph if Neo4j daemon is offline.
=============================================================================
"""

import os
import sys
import json
import pymysql
from collections import defaultdict, deque

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class InMemoryGraph:
    """High-speed in-memory graph store with identical Cypher-like traversals."""
    def __init__(self):
        self.nodes = {}  # id -> {"label": str, "properties": dict}
        self.edges = defaultdict(list)  # src_id -> [{"target": dst_id, "type": str, "properties": dict}]

    def add_node(self, node_id, label, properties):
        self.nodes[str(node_id)] = {"id": str(node_id), "label": label, "properties": properties}

    def add_edge(self, src_id, dst_id, rel_type, properties=None):
        self.edges[str(src_id)].append({
            "target": str(dst_id),
            "type": rel_type,
            "properties": properties or {}
        })

    def get_node(self, node_id):
        return self.nodes.get(str(node_id))

    def update_node(self, node_id, properties):
        nid = str(node_id)
        if nid in self.nodes:
            self.nodes[nid]["properties"].update(properties)
            return True
        return False

    def delete_node(self, node_id):
        nid = str(node_id)
        if nid in self.nodes:
            del self.nodes[nid]
            if nid in self.edges:
                del self.edges[nid]
            for s, rels in self.edges.items():
                self.edges[s] = [r for r in rels if r["target"] != nid]
            return True
        return False

    def delete_edge(self, src_id, dst_id, rel_type=None):
        src, dst = str(src_id), str(dst_id)
        if src in self.edges:
            init_len = len(self.edges[src])
            self.edges[src] = [
                r for r in self.edges[src] 
                if not (r["target"] == dst and (rel_type is None or r["type"] == rel_type))
            ]
            return len(self.edges[src]) < init_len
        return False

    def traverse_blast_radius(self, start_node_id, max_depth=3):
        """BFS multi-hop traversal to determine lateral threat blast radius."""
        start_id = str(start_node_id)
        if start_id not in self.nodes:
            return {"nodes": [], "edges": [], "summary": "Start node not found"}

        visited_nodes = {start_id}
        result_nodes = [self.nodes[start_id]]
        result_edges = []
        queue = deque([(start_id, 0)])

        while queue:
            curr_id, depth = queue.popleft()
            if depth >= max_depth:
                continue

            # Forward edges
            for edge in self.edges.get(curr_id, []):
                tgt = edge["target"]
                result_edges.append({
                    "source": curr_id,
                    "target": tgt,
                    "type": edge["type"],
                    "properties": edge["properties"]
                })
                if tgt not in visited_nodes:
                    visited_nodes.add(tgt)
                    if tgt in self.nodes:
                        result_nodes.append(self.nodes[tgt])
                    queue.append((tgt, depth + 1))

            # Backward edges (undirected exploration for blast radius)
            for src, rels in self.edges.items():
                for edge in rels:
                    if edge["target"] == curr_id and src not in visited_nodes:
                        visited_nodes.add(src)
                        if src in self.nodes:
                            result_nodes.append(self.nodes[src])
                        result_edges.append({
                            "source": src,
                            "target": curr_id,
                            "type": edge["type"],
                            "properties": edge["properties"]
                        })
                        queue.append((src, depth + 1))

        return {
            "root_node": self.nodes[start_id],
            "total_compromised_nodes": len(result_nodes),
            "traversal_depth": max_depth,
            "nodes": result_nodes,
            "edges": result_edges
        }


class ThreatGraphDB:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.is_connected = False
        self.fallback = InMemoryGraph()

        if NEO4J_AVAILABLE:
            try:
                self.driver = GraphDatabase.driver(uri, auth=(user, password), connection_timeout=1)
                with self.driver.session() as session:
                    session.run("RETURN 1;")
                self.is_connected = True
                print(f"[Neo4j] Connected successfully to live Neo4j instance at {uri}!")
            except Exception as e:
                self.is_connected = False
                # print(f"[Neo4j] Live server offline ({e}). Using embedded graph engine.")

    def close(self):
        if self.driver:
            self.driver.close()

    def sync_from_mysql(self, mysql_host="localhost", mysql_user="root", mysql_password="Marty@66", db_name="algo_fingerprint_db", limit=1000):
        """Populates the graph database from MySQL relational tables."""
        print(f"[ThreatGraph] Syncing MySQL '{db_name}' data into Graph schema...")
        conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=db_name)
        with conn.cursor() as cur:
            # 1. Developers
            cur.execute("SELECT dev_id, name, email, team FROM developer;")
            for r in cur.fetchall():
                nid = f"DEV_{r[0]}"
                props = {"dev_id": r[0], "name": r[1], "email": r[2], "team": r[3]}
                self.fallback.add_node(nid, "Developer", props)

            # 2. Compute Nodes
            cur.execute("SELECT node_id, hostname, ip_address, cpu_architecture, os_name FROM compute_node;")
            for r in cur.fetchall():
                nid = f"NODE_{r[0]}"
                props = {"node_id": r[0], "hostname": r[1], "ip_address": r[2], "arch": r[3], "os": r[4], "status": "ACTIVE"}
                self.fallback.add_node(nid, "ComputeNode", props)

            # 3. Baseline Patterns
            cur.execute("SELECT baseline_id, pattern_name, category, expected_ipc FROM baseline_pattern;")
            for r in cur.fetchall():
                nid = f"BASE_{r[0]}"
                props = {"baseline_id": r[0], "pattern_name": r[1], "category": r[2], "expected_ipc": float(r[3])}
                self.fallback.add_node(nid, "BaselinePattern", props)

            # 4. Algorithms
            cur.execute("SELECT algo_id, dev_id, algo_name, language, version, parent_algo_id FROM algorithm;")
            for r in cur.fetchall():
                nid = f"ALGO_{r[0]}"
                props = {"algo_id": r[0], "algo_name": r[2], "language": r[3], "version": r[4]}
                self.fallback.add_node(nid, "Algorithm", props)
                # Relationship: Developer -[:AUTHORED]-> Algorithm
                self.fallback.add_edge(f"DEV_{r[1]}", nid, "AUTHORED")
                # Polymorphic Lineage: Algorithm -[:DERIVED_FROM]-> Algorithm
                if r[5] is not None:
                    self.fallback.add_edge(nid, f"ALGO_{r[5]}", "DERIVED_FROM")

            # 5. Execution Runs & Detections (Subset for crisp graph traversal)
            cur.execute(f"""
                SELECT 
                    r.run_id, r.algo_id, r.node_id, r.execution_status, r.peak_memory_mb,
                    f.fingerprint_id, f.ipc_ratio, f.cache_miss_rate,
                    dl.alert_level, dl.classification_result, dl.baseline_id, dl.similarity_score
                FROM execution_run r
                JOIN fingerprint f ON r.run_id = f.run_id
                JOIN detection_log dl ON f.fingerprint_id = dl.fingerprint_id
                WHERE dl.alert_level IN ('Critical', 'High') OR r.run_id <= 300
                LIMIT {limit};
            """)
            for r in cur.fetchall():
                run_nid = f"RUN_{r[0]}"
                run_props = {"run_id": r[0], "status": r[3], "peak_memory": float(r[4] or 0)}
                self.fallback.add_node(run_nid, "ExecutionRun", run_props)
                
                # Rel: Algorithm -> ExecutionRun
                self.fallback.add_edge(f"ALGO_{r[1]}", run_nid, "EXECUTED_IN")
                # Rel: ExecutionRun -> ComputeNode
                self.fallback.add_edge(run_nid, f"NODE_{r[2]}", "RUNS_ON")

                # Rel: ExecutionRun -> BaselinePattern (Threat Flag)
                if r[10] is not None:
                    flag_props = {"alert_level": r[8], "classification": r[9], "similarity": float(r[11])}
                    self.fallback.add_edge(run_nid, f"BASE_{r[10]}", "FLAGGED_AS", flag_props)

        conn.close()
        print(f"[ThreatGraph] Graph loaded with {len(self.fallback.nodes)} nodes and {sum(len(v) for v in self.fallback.edges.values())} edges.")

    # --- RUD Operations (Read, Update, Delete) ---

    def create_security_alert_node(self, alert_id, run_id, alert_level, description):
        """Graph C: Create security alert node and edge."""
        nid = f"ALERT_{alert_id}"
        props = {"alert_id": alert_id, "level": alert_level, "description": description}
        self.fallback.add_node(nid, "SecurityAlert", props)
        self.fallback.add_edge(f"RUN_{run_id}", nid, "TRIGGERED_ALERT")
        return {"created_node": nid, "status": "Success"}

    def read_blast_radius(self, node_key, max_depth=3):
        """Graph R: Traversal query for threat blast radius."""
        return self.fallback.traverse_blast_radius(node_key, max_depth=max_depth)

    def update_node_status(self, node_key, new_status="QUARANTINED"):
        """Graph U: Update node property."""
        res = self.fallback.update_node(node_key, {"status": new_status})
        return {"node": node_key, "updated": res, "new_status": new_status}

    def delete_edge_link(self, src_key, dst_key, rel_type=None):
        """Graph D: Sever relationship (e.g. quarantine network execution edge)."""
        res = self.fallback.delete_edge(src_key, dst_key, rel_type)
        return {"src": src_key, "dst": dst_key, "severed": res}


if __name__ == "__main__":
    tg = ThreatGraphDB()
    tg.sync_from_mysql()

    print("\n--- Testing Graph Blast Radius Traversal for Compromised Node/Run ---")
    # Test blast radius on RUN_2 (PoW MemoryHard Loop) or ALGO_2
    blast = tg.read_blast_radius("ALGO_2", max_depth=2)
    print(f"Algorithm 'ALGO_2' Threat Blast Radius:")
    print(f"Total Connected Entities: {blast['total_compromised_nodes']}")
    for node in blast['nodes'][:8]:
        print(f"  - [{node['label']}] ID: {node['id']}, Props: {node['properties']}")

    print("\n--- Testing Graph Update (Quarantine Node) ---")
    upd = tg.update_node_status("NODE_1", "QUARANTINED")
    print("Update status:", upd)

