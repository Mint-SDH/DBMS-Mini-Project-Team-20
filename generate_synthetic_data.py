#!/usr/bin/env python3
"""
=============================================================================
SYNTHETIC DATA GENERATION ENGINE FOR ALGORITHMIC EXECUTION FINGERPRINTING
DBMS Mini Project | PES University (Group 20)
Authors: Sanyam Deven Hiran (PES2UG24CS446), Shashank A (PES2UG24CS461)
Database Engine: MySQL 8.0+
Database: algo_fingerprint_db
=============================================================================

This pipeline implements a semantically correlated synthetic data generator
using Faker, NumPy, and Python standard libraries. It models 5 core architectural
archetypes with realistic hardware performance counter distributions (IPC,
cache misses, branch mispredictions, memory footprints), guaranteeing strict
relational, chronological, and semantic integrity.

Topological Order:
  1. DEVELOPER (Independent Parent)
  2. COMPUTE_NODE (Independent Parent)
  3. BASELINE_PATTERN (Independent Parent)
  4. ALGORITHM (Child of DEVELOPER)
  5. EXECUTION_RUN (Child of ALGORITHM & COMPUTE_NODE)
  6. FINGERPRINT (1:1 Child of EXECUTION_RUN)
  7. DETECTION_LOG (Junction of FINGERPRINT & BASELINE_PATTERN)

Outputs:
  - Mode A: Standalone batched SQL script (.sql)
  - Mode B: 7 Individual CSV files ready for LOAD DATA INFILE (.csv)
=============================================================================
"""

import os
import sys
import csv
import math
import random
import hashlib
import argparse
from datetime import datetime, timedelta

# Import NumPy and Faker
try:
    import numpy as np
except ImportError:
    print("NumPy is required. Installing numpy...")
    os.system(f"{sys.executable} -m pip install numpy")
    import numpy as np

try:
    from faker import Faker
except ImportError:
    print("Faker is required. Installing faker...")
    os.system(f"{sys.executable} -m pip install faker")
    from faker import Faker


# -----------------------------------------------------------------------------
# 1. CORE DOMAIN CONFIGURATION & ARCHETYPES
# -----------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "num_developers": 75,
    "num_nodes": 35,
    "num_baselines": 25,
    "num_algorithms": 300,
    "num_runs": 4000,
    "seed": 42,
    "output_sql": "algo_fingerprint_data.sql",
    "csv_dir": "csv_data",
    "export_csv": True
}

# The 5 Core Reference Archetypes defined in the specification
REFERENCE_BASELINES = [
    {
        "id": 1,
        "pattern_name": "Matrix_Multiplication_BLAS",
        "category": "HPC_Compute",
        "expected_ipc": 2.85,
        "expected_cache_miss_rate": 3.20,
        "archetype": "HPC"
    },
    {
        "id": 2,
        "pattern_name": "Crypto_Miner_XMRig",
        "category": "Malware_Cryptojacking",
        "expected_ipc": 0.65,
        "expected_cache_miss_rate": 34.50,
        "archetype": "CRYPTO_MINER"
    },
    {
        "id": 3,
        "pattern_name": "TWAP_Order_Slicing",
        "category": "Financial_Algo",
        "expected_ipc": 1.40,
        "expected_cache_miss_rate": 6.80,
        "archetype": "FINANCIAL_HFT"
    },
    {
        "id": 4,
        "pattern_name": "QuickSort_In_Memory",
        "category": "Standard_Utility",
        "expected_ipc": 2.10,
        "expected_cache_miss_rate": 8.40,
        "archetype": "SORTING"
    },
    {
        "id": 5,
        "pattern_name": "Port_Scan_SYN_Flood",
        "category": "Network_Attack",
        "expected_ipc": 0.45,
        "expected_cache_miss_rate": 28.10,
        "archetype": "NETWORK_PROBE"
    }
]

# Additional benchmark baseline patterns for balanced larger workloads
SUPPLEMENTARY_BASELINES = [
    ("ResNet50_Conv2D_Inference", "AI_Inference", 2.20, 5.40, "HPC"),
    ("Transformer_SelfAttention_KEM", "AI_Inference", 1.95, 7.80, "HPC"),
    ("AES256_GCM_HardwareCipher", "Cryptography", 2.90, 1.80, "HPC"),
    ("Kyber768_PostQuantum_Encrypt", "Cryptography", 1.70, 9.40, "FINANCIAL_HFT"),
    ("BreadthFirstSearch_CSR", "Graph_Analytics", 0.58, 36.20, "NETWORK_PROBE"),
    ("PageRank_Iterative_CSR", "Graph_Analytics", 0.72, 29.50, "NETWORK_PROBE"),
    ("Dijkstra_MinHeap_SP", "Graph_Analytics", 0.85, 22.40, "SORTING"),
    ("RadixSort_Parallel_LSD", "Standard_Utility", 1.95, 7.90, "SORTING"),
    ("Bitonic_Sorting_Network", "Standard_Utility", 2.05, 6.50, "SORTING"),
    ("LSMTree_Compaction_Worker", "Database_Engine", 0.95, 22.80, "FINANCIAL_HFT"),
    ("BTree_Index_PointLookup", "Database_Engine", 1.25, 16.40, "FINANCIAL_HFT"),
    ("HashJoin_Probe_MultiThread", "Database_Engine", 1.35, 15.20, "FINANCIAL_HFT"),
    ("Zstd_Streaming_Compressor", "Data_Compression", 1.60, 12.50, "SORTING"),
    ("LZ4_Frame_Decompressor", "Data_Compression", 2.35, 4.20, "HPC"),
    ("Snappy_Block_Compressor", "Data_Compression", 2.15, 6.10, "HPC"),
    ("MonteCarlo_BlackScholes", "Financial_Algo", 2.10, 3.80, "FINANCIAL_HFT"),
    ("LimitOrderBook_Matcher", "Financial_Algo", 1.55, 7.20, "FINANCIAL_HFT"),
    ("BarnesHut_NBody_Gravity", "HPC_Compute", 1.80, 11.20, "HPC"),
    ("RandomX_CPU_ProofOfWork", "Malware_Cryptojacking", 0.52, 42.10, "CRYPTO_MINER"),
    ("Ethash_DAG_Cache_Trashing", "Malware_Cryptojacking", 0.48, 46.50, "CRYPTO_MINER")
]

TEAMS = [
    "Core Systems",
    "Security & HFT",
    "Infrastructure",
    "AI & Quant",
    "Compiler Toolchain"
]

REGIONS = ["us-east", "us-west", "eu-west", "eu-central", "ap-south", "ap-northeast"]
CPU_ARCHITECTURES = ["x86_64", "ARM64"]
OS_NAMES = ["Ubuntu 24.04 LTS", "RHEL 9.3", "Debian 12", "Arch Linux", "Ubuntu Core 22"]

LANGUAGES = ["C++", "Rust", "C", "Go", "Python"]
LANGUAGE_WEIGHTS = [0.35, 0.25, 0.15, 0.15, 0.10]

# Mapping Archetypes to Algorithm naming styles and realistic profiles
ARCHETYPE_ALGO_TEMPLATES = {
    "HPC": [
        "FastGEMM_Optimizer", "BLAS_MatrixMul_AVX", "ResNet_ConvKernel",
        "Cholesky_Factorizer", "FFT_CooleyTukey_SIMD", "MonteCarlo_SimEngine"
    ],
    "CRYPTO_MINER": [
        "Stealth_Hash_Worker", "XMR_RandomX_Core", "PoW_MemoryHard_Loop",
        "Silent_Cryptominer", "Shadow_Keccak_Miner", "Cryptonight_Runner"
    ],
    "FINANCIAL_HFT": [
        "Adaptive_TWAP_Bot", "VWAP_Execution_Slicer", "OrderBook_Matcher",
        "MonteCarlo_Pricer", "Arbitrage_Tick_Scanner", "MarketData_Parser"
    ],
    "SORTING": [
        "Parallel_Sort_Engine", "QuickSort_DualPivot", "Radix_LSD_Sorter",
        "TimSort_Native", "Bitonic_Sort_Kernel", "External_Merge_Sorter"
    ],
    "NETWORK_PROBE": [
        "Network_Packet_Probe", "RawSocket_SYN_Scanner", "ICMP_Port_Mapper",
        "Stealth_Sweep_Worker", "ARP_Traffic_Profiler", "Banner_Grabber_Async"
    ]
}


# -----------------------------------------------------------------------------
# 2. ESCAPE & FORMATTING UTILITIES
# -----------------------------------------------------------------------------

def escape_sql(val):
    """Escapes strings and formats None as NULL for raw SQL."""
    if val is None:
        return "NULL"
    if isinstance(val, (int, float, np.integer, np.floating)):
        return str(val)
    s = str(val).replace("\\", "\\\\").replace("'", "''")
    return f"'{s}'"

def format_csv_val(val):
    """Formats value for clean CSV output compatible with MySQL LOAD DATA INFILE."""
    if val is None:
        return ""
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    return str(val)


# -----------------------------------------------------------------------------
# 3. SYNTHETIC GENERATORS (TOPOLOGICAL ORDER)
# -----------------------------------------------------------------------------

def generate_developers(count, faker_instance):
    """Table 1: DEVELOPER (Independent Parent)"""
    developers = []
    used_emails = set()

    # Pre-seed mini project authors
    authors = [
        (1, "Sanyam Deven Hiran", "sanyam.hiran@techcorp.io", "Core Systems"),
        (2, "Shashank A", "shashank.a@techcorp.io", "Security & HFT")
    ]
    for dev in authors:
        developers.append(dev)
        used_emails.add(dev[2])

    dev_id = 3
    while len(developers) < count:
        first = faker_instance.first_name()
        last = faker_instance.last_name()
        name = f"{first} {last}"
        
        # Valid corporate email pattern: name.surname@techcorp.io
        suffix = f"{random.randint(10, 999)}" if random.random() < 0.3 else ""
        email = f"{first.lower()}.{last.lower()}{suffix}@techcorp.io".replace(" ", "")
        
        if email in used_emails:
            continue
        used_emails.add(email)

        team = random.choice(TEAMS)
        developers.append((dev_id, name, email, team))
        dev_id += 1

    return developers


def generate_compute_nodes(count):
    """Table 2: COMPUTE_NODE (Independent Parent)"""
    nodes = []
    used_hostnames = set()
    used_ips = set()

    node_id = 1
    while len(nodes) < count:
        region = random.choice(REGIONS)
        rack_id = f"{random.randint(1, 40):02d}"
        slot_id = f"{random.randint(1, 20):02d}"
        hostname = f"node-{region}-{rack_id}-{slot_id}"
        
        if hostname in used_hostnames:
            continue
        used_hostnames.add(hostname)

        # Generate unique private CIDR IP (10.x.x.x or 192.168.10.x)
        if random.random() < 0.6:
            ip = f"10.{random.randint(0, 100)}.{random.randint(1, 254)}.{random.randint(2, 254)}"
        else:
            ip = f"192.168.10.{random.randint(2, 254)}"
            
        if ip in used_ips:
            continue
        used_ips.add(ip)

        cpu_arch = random.choice(CPU_ARCHITECTURES)
        os_name = random.choice(OS_NAMES)

        nodes.append((node_id, hostname, ip, cpu_arch, os_name))
        node_id += 1

    return nodes


def generate_baseline_patterns(num_baselines):
    """Table 3: BASELINE_PATTERN (Independent Parent)"""
    baselines = []
    
    # 1. Add the 5 mandatory reference archetypes
    for ref in REFERENCE_BASELINES:
        baselines.append((
            ref["id"],
            ref["pattern_name"],
            ref["category"],
            float(ref["expected_ipc"]),
            float(ref["expected_cache_miss_rate"]),
            ref["archetype"]
        ))
        
    # 2. Add supplementary baselines if requested
    next_id = 6
    for item in SUPPLEMENTARY_BASELINES:
        if len(baselines) >= num_baselines:
            break
        p_name, cat, e_ipc, e_cache, arch = item
        baselines.append((next_id, p_name, cat, float(e_ipc), float(e_cache), arch))
        next_id += 1

    return baselines


def generate_algorithms(count, developers, baselines):
    """Table 4: ALGORITHM (Child of DEVELOPER)"""
    algorithms = []
    dev_ids = [d[0] for d in developers]
    archetypes = list(ARCHETYPE_ALGO_TEMPLATES.keys())
    
    # Map each baseline to its archetype for later correlation
    baseline_archetypes = {b[0]: b[5] for b in baselines}

    used_names = set()
    algo_id = 1

    for _ in range(count):
        dev_id = random.choice(dev_ids)
        # Select an archetype for this algorithm
        arch = random.choice(archetypes)
        template_name = random.choice(ARCHETYPE_ALGO_TEMPLATES[arch])
        
        # Ensure unique algorithm name
        cand_name = f"{template_name}_v{algo_id}" if template_name in used_names else template_name
        used_names.add(cand_name)
        
        # Realistic language distribution
        lang = np.random.choice(LANGUAGES, p=LANGUAGE_WEIGHTS)
        
        # Semantic versioning
        major = random.choice([0, 1, 1, 2, 3])
        minor = random.randint(0, 9)
        patch = random.randint(0, 15)
        version = f"v{major}.{minor}.{patch}"

        algorithms.append((algo_id, dev_id, cand_name, lang, version, arch))
        algo_id += 1

    return algorithms


def generate_execution_runs(count, algorithms, nodes):
    """Table 5: EXECUTION_RUN (Child of ALGORITHM & COMPUTE_NODE)"""
    runs = []
    algo_lookup = {a[0]: a for a in algorithms}
    algo_ids = list(algo_lookup.keys())
    node_ids = [n[0] for n in nodes]

    # Past 30 days window
    now = datetime.now()
    window_start = now - timedelta(days=30)
    total_seconds = int((now - window_start).total_seconds())

    run_id = 1
    for _ in range(count):
        algo_id = random.choice(algo_ids)
        node_id = random.choice(node_ids)
        algo = algo_lookup[algo_id]
        arch = algo[5]  # Archetype

        # Start time within past 30 days
        rand_offset = random.randint(0, max(1, total_seconds - 7200))
        start_time = window_start + timedelta(seconds=rand_offset)

        # Archetype-dependent status and peak memory
        if arch == "CRYPTO_MINER":
            # Cryptominers often get terminated by watchdog or complete stealthily
            status = np.random.choice(["Completed", "Terminated", "Failed"], p=[0.45, 0.45, 0.10])
            peak_memory = round(float(np.random.uniform(2048.00, 8192.00)), 2)
            duration_sec = random.randint(180, 7100)
        elif arch == "NETWORK_PROBE":
            # Network probes have low memory and can fail or be terminated
            status = np.random.choice(["Completed", "Terminated", "Failed"], p=[0.60, 0.30, 0.10])
            peak_memory = round(float(np.random.uniform(64.00, 255.00)), 2)
            duration_sec = random.randint(30, 900)
        elif arch == "HPC":
            # HPC matrix engines use significant memory and usually complete
            status = np.random.choice(["Completed", "Running", "Failed"], p=[0.90, 0.05, 0.05])
            peak_memory = round(float(np.random.uniform(1024.00, 16384.00)), 2)
            duration_sec = random.randint(300, 7200)
        elif arch == "FINANCIAL_HFT":
            # HFT algorithms run continuous order slicing with tight memory
            status = np.random.choice(["Completed", "Running", "Terminated"], p=[0.85, 0.10, 0.05])
            peak_memory = round(float(np.random.uniform(256.00, 4096.00)), 2)
            duration_sec = random.randint(60, 3600)
        else: # SORTING
            status = np.random.choice(["Completed", "Failed"], p=[0.92, 0.08])
            peak_memory = round(float(np.random.uniform(128.00, 4096.00)), 2)
            duration_sec = random.randint(30, 1800)

        # Strict chronological consistency: end_time > start_time (30s to 2h)
        if status == "Running":
            end_time = None
        else:
            end_time = start_time + timedelta(seconds=duration_sec)

        runs.append((run_id, algo_id, node_id, start_time, end_time, status, peak_memory, arch))
        run_id += 1

    return runs


def generate_fingerprints(runs):
    """
    Table 6: FINGERPRINT (Strict 1:1 Child of EXECUTION_RUN for profiled runs)
    Only Completed and Terminated runs produce a completed hardware fingerprint trace.
    """
    fingerprints = []
    used_hashes = set()
    fp_id = 1

    for run in runs:
        run_id, algo_id, node_id, start_time, end_time, status, peak_mem, arch = run
        
        # Only profiled runs (Completed or Terminated) receive fingerprints
        if status not in ("Completed", "Terminated"):
            continue

        # Strict domain physics based on the 5 Archetypes:
        if arch == "HPC":
            # High IPC, very low cache misses, very low branch mispredictions
            ipc = round(float(np.random.uniform(2.500, 3.500)), 3)
            cache_miss = round(float(np.random.uniform(1.50, 5.00)), 2)
            branch_mispred = round(float(np.random.uniform(0.50, 2.00)), 2)
        elif arch == "CRYPTO_MINER":
            # Low IPC, extreme cache misses (memory-hard PoW), high branch mispredictions
            ipc = round(float(np.random.uniform(0.500, 0.850)), 3)
            cache_miss = round(float(np.random.uniform(30.00, 48.00)), 2)
            branch_mispred = round(float(np.random.uniform(12.00, 22.00)), 2)
        elif arch == "NETWORK_PROBE":
            # Very low IPC (socket I/O stalls), elevated cache misses, high branch mispredictions
            ipc = round(float(np.random.uniform(0.300, 0.600)), 3)
            cache_miss = round(float(np.random.uniform(20.00, 35.00)), 2)
            branch_mispred = round(float(np.random.uniform(10.00, 18.00)), 2)
        elif arch == "FINANCIAL_HFT":
            # Moderate IPC, controlled cache misses, low branch mispredictions
            ipc = round(float(np.random.uniform(1.200, 1.700)), 3)
            cache_miss = round(float(np.random.uniform(5.00, 9.00)), 2)
            branch_mispred = round(float(np.random.uniform(2.00, 5.00)), 2)
        else: # SORTING
            # Good IPC, moderate cache misses, low-to-moderate branch mispredictions
            ipc = round(float(np.random.uniform(1.900, 2.400)), 3)
            cache_miss = round(float(np.random.uniform(6.00, 11.00)), 2)
            branch_mispred = round(float(np.random.uniform(1.50, 4.00)), 2)

        # Deterministic unique 64-character SHA-256 signature hash
        hash_seed = f"SIG:{run_id}:{algo_id}:{node_id}:{ipc}:{cache_miss}:{branch_mispred}"
        sig_hash = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()
        
        while sig_hash in used_hashes:
            hash_seed += ":salt"
            sig_hash = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()
        used_hashes.add(sig_hash)

        fingerprints.append((fp_id, run_id, ipc, cache_miss, branch_mispred, sig_hash, arch))
        fp_id += 1

    return fingerprints


def generate_detection_logs(fingerprints, baselines):
    """
    Table 7: DETECTION_LOG (Junction of FINGERPRINT & BASELINE_PATTERN)
    Correlates execution fingerprints against baselines with semantic accuracy.
    """
    detection_logs = []
    det_id = 1

    # Organize baselines by archetype for direct congruent comparisons
    baselines_by_arch = {}
    baseline_lookup = {}
    for b in baselines:
        b_id, p_name, cat, e_ipc, e_cache, arch = b
        baseline_lookup[b_id] = b
        baselines_by_arch.setdefault(arch, []).append(b)

    all_baseline_ids = list(baseline_lookup.keys())

    for fp in fingerprints:
        fp_id, run_id, ipc, cache_miss, branch_mispred, sig_hash, fp_arch = fp

        # 1. Primary evaluation: compare against its matching archetype baseline
        matching_baselines = baselines_by_arch.get(fp_arch, baselines)
        primary_baseline = random.choice(matching_baselines)
        b_id = primary_baseline[0]

        # Calculate high similarity and proper alerts according to Section 4 specifications
        if fp_arch == "HPC":
            sim_score = round(float(np.random.uniform(94.00, 99.50)), 2)
            alert = "Info"
            classification = "Verified_Safe"
        elif fp_arch == "CRYPTO_MINER":
            sim_score = round(float(np.random.uniform(91.00, 98.00)), 2)
            alert = "Critical"
            classification = "Malicious_Cryptojacking"
        elif fp_arch == "NETWORK_PROBE":
            sim_score = round(float(np.random.uniform(88.00, 96.00)), 2)
            alert = "High"
            classification = "Port_Scan_Detected"
        elif fp_arch == "FINANCIAL_HFT":
            sim_score = round(float(np.random.uniform(92.00, 98.50)), 2)
            alert = "Info"
            classification = "Verified_Safe"
        else: # SORTING
            sim_score = round(float(np.random.uniform(93.00, 99.00)), 2)
            alert = "Info"
            classification = "Verified_Safe"

        # Inject realistic occasional behavioral drift / overhead anomaly (approx 5% of safe runs)
        if fp_arch in ("HPC", "FINANCIAL_HFT", "SORTING") and random.random() < 0.06:
            sim_score = round(float(np.random.uniform(70.00, 84.00)), 2)
            alert = random.choice(["Low", "Medium"])
            classification = random.choice(["Behavioral_Drift", "Anomalous_Overhead"])

        detection_logs.append((det_id, fp_id, b_id, sim_score, alert, classification))
        det_id += 1

        # 2. Secondary evaluation: compare against 1 or 2 other contrasting baselines (cross-validation)
        other_b_ids = [bid for bid in all_baseline_ids if bid != b_id]
        if other_b_ids:
            num_extra = random.choice([1, 2])
            for sec_bid in random.sample(other_b_ids, min(num_extra, len(other_b_ids))):
                sec_b = baseline_lookup[sec_bid]
                # Compare distance between fingerprint and secondary baseline
                diff_ipc = abs(ipc - sec_b[3]) / max(sec_b[3], 1.0)
                diff_cache = abs(cache_miss - sec_b[4]) / max(sec_b[4], 1.0)
                sec_sim = max(60.00, min(89.00, round(100.00 - ((diff_ipc + diff_cache) * 35.0), 2)))

                # Determine alert based on secondary classification
                sec_is_threat = (sec_b[5] in ("CRYPTO_MINER", "NETWORK_PROBE"))
                if sec_is_threat:
                    if sec_sim > 82.00:
                        sec_alert = "Critical" if sec_b[5] == "CRYPTO_MINER" else "High"
                        sec_class = "Malicious_Cryptojacking" if sec_b[5] == "CRYPTO_MINER" else "Port_Scan_Detected"
                    else:
                        sec_alert = "Low"
                        sec_class = "Behavioral_Drift"
                else:
                    if sec_sim >= 85.00:
                        sec_alert = "Info"
                        sec_class = "Verified_Safe"
                    elif sec_sim >= 70.00:
                        sec_alert = "Low"
                        sec_class = "Behavioral_Drift"
                    else:
                        sec_alert = "Medium"
                        sec_class = "Anomalous_Overhead"

                detection_logs.append((det_id, fp_id, sec_bid, sec_sim, sec_alert, sec_class))
                det_id += 1

    return detection_logs


# -----------------------------------------------------------------------------
# 4. OUTPUT WRITERS (MODE A: SQL SCRIPT & MODE B: CSV DUMPS)
# -----------------------------------------------------------------------------

def write_sql_script(filepath, developers, nodes, baselines, algorithms, runs, fingerprints, detection_logs):
    """
    Mode A: Generates clean, batched SQL seed script for MySQL 8.0+.
    Uses transactions, disables foreign key checks for speed, and preserves topological order.
    """
    BATCH_SIZE = 250

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("-- ====================================================================\n")
        f.write("-- Algorithmic Execution Fingerprinting - Synthetic Dataset Seed\n")
        f.write("-- DBMS Mini Project | PES University (Group 20)\n")
        f.write(f"-- Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- Database: algo_fingerprint_db\n")
        f.write("-- ====================================================================\n\n")

        f.write("USE algo_fingerprint_db;\n\n")
        f.write("SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;\n")
        f.write("SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';\n")
        f.write("START TRANSACTION;\n\n")

        # 1. DEVELOPER
        f.write("-- 1. DEVELOPER\n")
        for i in range(0, len(developers), BATCH_SIZE):
            batch = developers[i:i + BATCH_SIZE]
            vals = [f"({d[0]}, {escape_sql(d[1])}, {escape_sql(d[2])}, {escape_sql(d[3])})" for d in batch]
            f.write("INSERT INTO DEVELOPER (dev_id, name, email, team) VALUES\n  " + ",\n  ".join(vals) + ";\n")
        f.write("\n")

        # 2. COMPUTE_NODE
        f.write("-- 2. COMPUTE_NODE\n")
        for i in range(0, len(nodes), BATCH_SIZE):
            batch = nodes[i:i + BATCH_SIZE]
            vals = [f"({n[0]}, {escape_sql(n[1])}, {escape_sql(n[2])}, {escape_sql(n[3])}, {escape_sql(n[4])})" for n in batch]
            f.write("INSERT INTO COMPUTE_NODE (node_id, hostname, ip_address, cpu_architecture, os_name) VALUES\n  " + ",\n  ".join(vals) + ";\n")
        f.write("\n")

        # 3. BASELINE_PATTERN
        f.write("-- 3. BASELINE_PATTERN\n")
        for i in range(0, len(baselines), BATCH_SIZE):
            batch = baselines[i:i + BATCH_SIZE]
            vals = [f"({b[0]}, {escape_sql(b[1])}, {escape_sql(b[2])}, {b[3]:.2f}, {b[4]:.2f})" for b in batch]
            f.write("INSERT INTO BASELINE_PATTERN (baseline_id, pattern_name, category, expected_ipc, expected_cache_miss_rate) VALUES\n  " + ",\n  ".join(vals) + ";\n")
        f.write("\n")

        # 4. ALGORITHM
        f.write("-- 4. ALGORITHM\n")
        for i in range(0, len(algorithms), BATCH_SIZE):
            batch = algorithms[i:i + BATCH_SIZE]
            vals = [f"({a[0]}, {a[1]}, {escape_sql(a[2])}, {escape_sql(a[3])}, {escape_sql(a[4])})" for a in batch]
            f.write("INSERT INTO ALGORITHM (algo_id, dev_id, algo_name, language, version) VALUES\n  " + ",\n  ".join(vals) + ";\n")
        f.write("\n")

        # 5. EXECUTION_RUN
        f.write("-- 5. EXECUTION_RUN\n")
        for i in range(0, len(runs), BATCH_SIZE):
            batch = runs[i:i + BATCH_SIZE]
            vals = []
            for r in batch:
                s_time = r[3].strftime("%Y-%m-%d %H:%M:%S")
                e_time = r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None
                vals.append(f"({r[0]}, {r[1]}, {r[2]}, {escape_sql(s_time)}, {escape_sql(e_time)}, {escape_sql(r[5])}, {escape_sql(r[6])})")
            f.write("INSERT INTO EXECUTION_RUN (run_id, algo_id, node_id, start_time, end_time, execution_status, peak_memory_mb) VALUES\n  " + ",\n  ".join(vals) + ";\n")
        f.write("\n")

        # 6. FINGERPRINT
        f.write("-- 6. FINGERPRINT\n")
        for i in range(0, len(fingerprints), BATCH_SIZE):
            batch = fingerprints[i:i + BATCH_SIZE]
            vals = [f"({fp[0]}, {fp[1]}, {fp[2]:.3f}, {fp[3]:.2f}, {fp[4]:.2f}, {escape_sql(fp[5])})" for fp in batch]
            f.write("INSERT INTO FINGERPRINT (fingerprint_id, run_id, ipc_ratio, cache_miss_rate, branch_misprediction_rate, signature_hash) VALUES\n  " + ",\n  ".join(vals) + ";\n")
        f.write("\n")

        # 7. DETECTION_LOG
        f.write("-- 7. DETECTION_LOG\n")
        for i in range(0, len(detection_logs), BATCH_SIZE):
            batch = detection_logs[i:i + BATCH_SIZE]
            vals = [f"({dl[0]}, {dl[1]}, {dl[2]}, {dl[3]:.2f}, {escape_sql(dl[4])}, {escape_sql(dl[5])})" for dl in batch]
            f.write("INSERT INTO DETECTION_LOG (detection_id, fingerprint_id, baseline_id, similarity_score, alert_level, classification_result) VALUES\n  " + ",\n  ".join(vals) + ";\n")
        f.write("\n")

        f.write("COMMIT;\n")
        f.write("SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;\n")
        f.write("SET SQL_MODE=@OLD_SQL_MODE;\n\n")


def write_csv_dumps(output_dir, developers, nodes, baselines, algorithms, runs, fingerprints, detection_logs):
    """
    Mode B: Generates 7 clean CSV files ready for MySQL LOAD DATA INFILE.
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. developer.csv
    with open(os.path.join(output_dir, "developer.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["dev_id", "name", "email", "team"])
        for d in developers:
            writer.writerow([d[0], d[1], d[2], d[3]])

    # 2. compute_node.csv
    with open(os.path.join(output_dir, "compute_node.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["node_id", "hostname", "ip_address", "cpu_architecture", "os_name"])
        for n in nodes:
            writer.writerow([n[0], n[1], n[2], n[3], n[4]])

    # 3. baseline_pattern.csv
    with open(os.path.join(output_dir, "baseline_pattern.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["baseline_id", "pattern_name", "category", "expected_ipc", "expected_cache_miss_rate"])
        for b in baselines:
            writer.writerow([b[0], b[1], b[2], f"{b[3]:.2f}", f"{b[4]:.2f}"])

    # 4. algorithm.csv
    with open(os.path.join(output_dir, "algorithm.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["algo_id", "dev_id", "algo_name", "language", "version"])
        for a in algorithms:
            writer.writerow([a[0], a[1], a[2], a[3], a[4]])

    # 5. execution_run.csv
    with open(os.path.join(output_dir, "execution_run.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["run_id", "algo_id", "node_id", "start_time", "end_time", "execution_status", "peak_memory_mb"])
        for r in runs:
            s_time = r[3].strftime("%Y-%m-%d %H:%M:%S")
            e_time = r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else "\\N"
            writer.writerow([r[0], r[1], r[2], s_time, e_time, r[5], r[6]])

    # 6. fingerprint.csv
    with open(os.path.join(output_dir, "fingerprint.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fingerprint_id", "run_id", "ipc_ratio", "cache_miss_rate", "branch_misprediction_rate", "signature_hash"])
        for fp in fingerprints:
            writer.writerow([fp[0], fp[1], f"{fp[2]:.3f}", f"{fp[3]:.2f}", f"{fp[4]:.2f}", fp[5]])

    # 7. detection_log.csv
    with open(os.path.join(output_dir, "detection_log.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["detection_id", "fingerprint_id", "baseline_id", "similarity_score", "alert_level", "classification_result"])
        for dl in detection_logs:
            writer.writerow([dl[0], dl[1], dl[2], f"{dl[3]:.2f}", dl[4], dl[5]])


# -----------------------------------------------------------------------------
# 5. CLI & MAIN PIPELINE ENTRY POINT
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Synthetic Data Generation Pipeline for Algorithmic Execution Fingerprinting (MySQL 8.0+)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--developers", type=int, default=DEFAULT_CONFIG["num_developers"], help="Number of developers to generate")
    parser.add_argument("--nodes", type=int, default=DEFAULT_CONFIG["num_nodes"], help="Number of compute nodes to generate")
    parser.add_argument("--baselines", type=int, default=DEFAULT_CONFIG["num_baselines"], help="Number of baseline patterns (min 5)")
    parser.add_argument("--algorithms", type=int, default=DEFAULT_CONFIG["num_algorithms"], help="Number of algorithms to generate")
    parser.add_argument("--runs", type=int, default=DEFAULT_CONFIG["num_runs"], help="Number of execution runs to generate")
    parser.add_argument("--seed", type=int, default=DEFAULT_CONFIG["seed"], help="Random seed for reproducible dataset")
    parser.add_argument("--output-sql", type=str, default=DEFAULT_CONFIG["output_sql"], help="Path for Mode A generated SQL script")
    parser.add_argument("--csv-dir", type=str, default=DEFAULT_CONFIG["csv_dir"], help="Directory for Mode B CSV dumps")
    parser.add_argument("--no-csv", action="store_true", help="Disable CSV export")

    args = parser.parse_args()

    # Seed pseudorandom generators
    random.seed(args.seed)
    np.random.seed(args.seed)
    faker = Faker()
    Faker.seed(args.seed)

    print("=" * 70)
    print("ALGORITHMIC EXECUTION FINGERPRINTING - SYNTHETIC DATA ENGINE")
    print("DBMS Mini Project | PES University (Group 20)")
    print("=" * 70)

    print(f"\n[1/7] Generating {args.developers} Developers (Teams: {', '.join(TEAMS)})...")
    developers = generate_developers(args.developers, faker)

    print(f"[2/7] Generating {args.nodes} Compute Nodes (x86_64, ARM64 across {len(REGIONS)} regions)...")
    nodes = generate_compute_nodes(args.nodes)

    print(f"[3/7] Generating {args.baselines} Baseline Patterns (HPC, Cryptojacking, HFT, Sorting, Network)...")
    baselines = generate_baseline_patterns(max(5, args.baselines))

    print(f"[4/7] Generating {args.algorithms} Registered Algorithms...")
    algorithms = generate_algorithms(args.algorithms, developers, baselines)

    print(f"[5/7] Generating {args.runs} Execution Runs (Past 30-day window, chronological duration)...")
    runs = generate_execution_runs(args.runs, algorithms, nodes)

    completed_runs = sum(1 for r in runs if r[5] in ("Completed", "Terminated"))
    print(f"[6/7] Synthesizing Hardware Fingerprints for {completed_runs} profiled runs (Strict 1:1)...")
    fingerprints = generate_fingerprints(runs)

    print(f"[7/7] Generating Multi-Baseline Detection & Anomaly Logs...")
    detection_logs = generate_detection_logs(fingerprints, baselines)

    # Mode A: SQL Script
    sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output_sql)
    print(f"\n[Mode A] Writing batched SQL script to: {sql_path} ...")
    write_sql_script(sql_path, developers, nodes, baselines, algorithms, runs, fingerprints, detection_logs)
    sql_size_mb = os.path.getsize(sql_path) / (1024 * 1024)

    # Mode B: CSV Dumps
    if not args.no_csv:
        csv_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.csv_dir)
        print(f"[Mode B] Exporting 7 CSV files to directory: {csv_dir_path} ...")
        write_csv_dumps(csv_dir_path, developers, nodes, baselines, algorithms, runs, fingerprints, detection_logs)

    # Print Summary Report
    print("\n" + "=" * 70)
    print("SYNTHETIC DATASET GENERATION SUMMARY:")
    print("=" * 70)
    print(f" 1. DEVELOPER         : {len(developers):>7} rows")
    print(f" 2. COMPUTE_NODE      : {len(nodes):>7} rows")
    print(f" 3. BASELINE_PATTERN  : {len(baselines):>7} rows (5 Core Archetypes + Benchmarks)")
    print(f" 4. ALGORITHM         : {len(algorithms):>7} rows (~{len(algorithms)//len(developers)} per developer)")
    print(f" 5. EXECUTION_RUN     : {len(runs):>7} rows (Completed: {sum(1 for r in runs if r[5]=='Completed')}, Terminated: {sum(1 for r in runs if r[5]=='Terminated')}, Running: {sum(1 for r in runs if r[5]=='Running')}, Failed: {sum(1 for r in runs if r[5]=='Failed')})")
    print(f" 6. FINGERPRINT       : {len(fingerprints):>7} rows (Strictly 1:1 with profiled runs)")
    print(f" 7. DETECTION_LOG     : {len(detection_logs):>7} rows (Archetype & Cross-Baseline logs)")
    total_tuples = len(developers) + len(nodes) + len(baselines) + len(algorithms) + len(runs) + len(fingerprints) + len(detection_logs)
    print(f" --------------------------------------------------------------------")
    print(f" TOTAL TUPLES         : {total_tuples:>7} rows")
    print(f" Mode A (SQL Dump)    : {args.output_sql} ({sql_size_mb:.2f} MB)")
    if not args.no_csv:
        print(f" Mode B (CSV Dumps)   : {args.csv_dir}/ (7 individual .csv tables)")
    print("=" * 70)


if __name__ == "__main__":
    main()
