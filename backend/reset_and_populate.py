#!/usr/bin/env python3
"""
=============================================================================
ALL-IN-ONE RESET & POPULATE PIPELINE FOR algo_fingerprint_db
DBMS Mini Project | PES University (Group 20)
=============================================================================

This script:
1. Generates a completely fresh synthetic dataset using the 5 core archetypes.
2. Connects to MySQL (algo_fingerprint_db).
3. Safely TRUNCATES (clears) all existing rows across all 7 tables.
4. Inserts the newly generated dataset in strict topological order.
5. Verifies and displays the final row counts for all tables.
=============================================================================
"""

import os
import sys
import time
import getpass
import argparse
import pymysql

# Import generation routines from generate_synthetic_data.py
from generate_synthetic_data import (
    DEFAULT_CONFIG,
    generate_developers,
    generate_compute_nodes,
    generate_baseline_patterns,
    generate_algorithms,
    generate_execution_runs,
    generate_fingerprints,
    generate_detection_logs,
    write_sql_script,
    write_csv_dumps,
    TEAMS,
    REGIONS
)
from insert_to_db import parse_sql_statements

def main():
    parser = argparse.ArgumentParser(description="Reset and populate algo_fingerprint_db with fresh synthetic data")
    parser.add_argument("--password", "-p", type=str, default=None, help="MySQL root password (if omitted, will prompt)")
    parser.add_argument("--host", type=str, default="localhost", help="MySQL Host (default: localhost)")
    parser.add_argument("--port", type=int, default=3306, help="MySQL Port (default: 3306)")
    parser.add_argument("--user", "-u", type=str, default="root", help="MySQL User (default: root)")
    parser.add_argument("--database", "-d", type=str, default="algo_fingerprint_db", help="Target database")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (defaults to current time)")
    args = parser.parse_args()

    print("=" * 70)
    print("ALGO FINGERPRINT DB: DATABASE RESET & FRESH POPULATION PIPELINE")
    print("DBMS Mini Project | PES University (Group 20)")
    print("=" * 70)

    # 1. Credentials
    password = args.password
    if password is None:
        password = getpass.getpass(f"Enter MySQL password for {args.user}@{args.host}: ")

    # 2. Test Connection
    print(f"\n[1/5] Connecting to MySQL database '{args.database}' on {args.host}:{args.port}...")
    try:
        connection = pymysql.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=password,
            database=args.database,
            charset="utf8mb4",
            autocommit=False
        )
        print("Connected successfully!")
    except Exception as e:
        print(f"\nConnection failed: {e}")
        print("Please check your password and ensure MySQL server is running.")
        sys.exit(1)

    # 3. Clear Existing Data
    print("\n[2/5] Clearing all existing tuples from database tables...")
    tables_to_clear = [
        "DETECTION_LOG",
        "FINGERPRINT",
        "EXECUTION_RUN",
        "ALGORITHM",
        "BASELINE_PATTERN",
        "COMPUTE_NODE",
        "DEVELOPER"
    ]
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            for table in tables_to_clear:
                cursor.execute(f"TRUNCATE TABLE {table};")
                print(f"  Truncated table `{table}`")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            connection.commit()
        print("All tables cleared successfully! Database is completely empty.")
    except Exception as e:
        connection.rollback()
        print(f"Error clearing tables: {e}")
        connection.close()
        sys.exit(1)

    # 4. Generate Fresh Synthetic Data
    seed = args.seed if args.seed is not None else int(time.time())
    print(f"\n[3/5] Generating fresh synthetic dataset (Seed: {seed})...")
    import random
    import numpy as np
    from faker import Faker

    random.seed(seed)
    np.random.seed(seed % (2**32))
    faker = Faker()
    Faker.seed(seed)

    developers = generate_developers(DEFAULT_CONFIG["num_developers"], faker)
    nodes = generate_compute_nodes(DEFAULT_CONFIG["num_nodes"])
    baselines = generate_baseline_patterns(DEFAULT_CONFIG["num_baselines"])
    algorithms = generate_algorithms(DEFAULT_CONFIG["num_algorithms"], developers, baselines)
    runs = generate_execution_runs(DEFAULT_CONFIG["num_runs"], algorithms, nodes)
    fingerprints = generate_fingerprints(runs)
    detection_logs = generate_detection_logs(fingerprints, baselines)

    sql_path = DEFAULT_CONFIG["output_sql"]
    csv_dir = DEFAULT_CONFIG["csv_dir"]
    
    write_sql_script(sql_path, developers, nodes, baselines, algorithms, runs, fingerprints, detection_logs)
    write_csv_dumps(csv_dir, developers, nodes, baselines, algorithms, runs, fingerprints, detection_logs)
    print(f"  Synthesized {len(developers) + len(nodes) + len(baselines) + len(algorithms) + len(runs) + len(fingerprints) + len(detection_logs)} tuples.")
    print(f"  Updated SQL script: {DEFAULT_CONFIG['output_sql']}")
    print(f"  Updated CSV dumps in: {DEFAULT_CONFIG['csv_dir']}/")

    # 5. Insert New Data into Database
    print("\n[4/5] Inserting fresh dataset into MySQL...")
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    statements = parse_sql_statements(sql_content)
    total_stmts = len(statements)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            for idx, stmt in enumerate(statements, start=1):
                cursor.execute(stmt)
                if idx % 15 == 0 or idx == total_stmts:
                    pct = (idx / total_stmts) * 100
                    print(f"  Inserted batch {idx}/{total_stmts} ({pct:.1f}%)...")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            connection.commit()
        print("Data committed successfully!")
    except Exception as e:
        connection.rollback()
        print(f"Error during insertion: {e}")
        connection.close()
        sys.exit(1)

    # 6. Verify Row Counts
    print("\n[5/5] Final Database Row Count Verification:")
    print("=" * 70)
    try:
        with connection.cursor() as cursor:
            verify_tables = [
                "DEVELOPER",
                "COMPUTE_NODE",
                "BASELINE_PATTERN",
                "ALGORITHM",
                "EXECUTION_RUN",
                "FINGERPRINT",
                "DETECTION_LOG"
            ]
            total_db_rows = 0
            for tbl in verify_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
                cnt = cursor.fetchone()[0]
                total_db_rows += cnt
                print(f"  {tbl:<22}: {cnt:>8} rows")
            print("-" * 70)
            print(f"  TOTAL RECORDS IN DB   : {total_db_rows:>8} rows")
    finally:
        connection.close()

    print("=" * 70)
    print("Database reset and repopulation completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
