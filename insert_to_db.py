#!/usr/bin/env python3
"""
Direct Database Inserter for algo_fingerprint_db
DBMS Mini Project - Algorithmic Execution Fingerprinting

Reads 'algo_fingerprint_data.sql' and executes the batch inserts into your local MySQL database.
"""

import os
import sys
import getpass
import pymysql

SQL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "algo_fingerprint_data.sql")

def parse_sql_statements(sql_content):
    """
    Strips comment lines and empty lines, then splits by semicolon into valid SQL statements.
    """
    clean_lines = []
    for line in sql_content.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or not stripped:
            continue
        clean_lines.append(line)
    
    full_clean_sql = "\n".join(clean_lines)
    statements = [stmt.strip() for stmt in full_clean_sql.split(";") if stmt.strip()]
    return statements

def main():
    print("=" * 65)
    print("Algo Fingerprint DB - MySQL Direct Data Inserter")
    print("DBMS Mini Project | PES University")
    print("=" * 65)

    if not os.path.exists(SQL_FILE):
        print(f"Error: {SQL_FILE} not found! Please run 'python generate_synthetic_data.py' first.")
        sys.exit(1)

    host = input("MySQL Host [localhost]: ").strip() or "localhost"
    port_str = input("MySQL Port [3306]: ").strip() or "3306"
    port = int(port_str)
    user = input("MySQL User [root]: ").strip() or "root"
    password = getpass.getpass(f"Enter password for {user}@{host}: ")
    db_name = "algo_fingerprint_db"

    print(f"\nConnecting to MySQL server at {host}:{port}...")
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            charset="utf8mb4",
            autocommit=False
        )
        print("Connected successfully!")
    except Exception as e:
        print(f"\nConnection failed: {e}")
        print("\nTip: Make sure MySQL Server is running and your credentials are correct.")
        sys.exit(1)

    try:
        with connection.cursor() as cursor:
            # Ask to clear existing data to prevent duplicate key errors
            clear_existing = input("\nClear existing data before inserting? (y/n) [y]: ").strip().lower()
            if clear_existing in ("", "y", "yes"):
                print("Clearing existing records...")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                tables_to_clear = [
                    "DETECTION_LOG", "FINGERPRINT", "EXECUTION_RUN",
                    "ALGORITHM", "BASELINE_PATTERN", "COMPUTE_NODE", "DEVELOPER"
                ]
                for tbl in tables_to_clear:
                    cursor.execute(f"TRUNCATE TABLE {tbl};")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                connection.commit()
                print("Tables cleared successfully.")

            print("\nReading and parsing SQL file...")
            with open(SQL_FILE, "r", encoding="utf-8") as f:
                sql_content = f.read()

            statements = parse_sql_statements(sql_content)
            total_statements = len(statements)
            print(f"Executing {total_statements} SQL statements into '{db_name}'...")

            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            for idx, stmt in enumerate(statements, start=1):
                cursor.execute(stmt)
                if idx % 10 == 0 or idx == total_statements:
                    percent = (idx / total_statements) * 100
                    print(f"  Progress: {idx}/{total_statements} statements executed ({percent:.1f}%)...")

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            connection.commit()
            print("\nData committed successfully!")

            # Verify row counts
            print("\n" + "=" * 65)
            print("DATABASE VERIFICATION (CURRENT ROW COUNTS):")
            print("=" * 65)
            tables = [
                "DEVELOPER",
                "COMPUTE_NODE",
                "BASELINE_PATTERN",
                "ALGORITHM",
                "EXECUTION_RUN",
                "FINGERPRINT",
                "DETECTION_LOG"
            ]
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f" {table:<20}: {count:>8} rows")
            print("=" * 65)

    except Exception as e:
        connection.rollback()
        print(f"\nAn error occurred during insertion: {e}")
        print("Rolled back any uncommitted changes.")
        sys.exit(1)
    finally:
        connection.close()
        print("\nConnection closed. Done!")

if __name__ == "__main__":
    main()
