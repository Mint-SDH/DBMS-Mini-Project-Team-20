-- ====================================================================
-- ALGORITHMIC EXECUTION FINGERPRINTING & RUNTIME THREAT DETECTION
-- Relational DDL Schema, Keys, Integrity Constraints & RBAC
-- Author: Sanyam Deven Hiran (PES2UG24CS446) | Group 20
-- Engine: MySQL 8.0+
-- Database: algo_fingerprint_db
-- ====================================================================

CREATE DATABASE IF NOT EXISTS algo_fingerprint_db;
USE algo_fingerprint_db;

-- 1. DEVELOPER (Strong Entity)
CREATE TABLE IF NOT EXISTS DEVELOPER (
    dev_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    team VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. COMPUTE_NODE (Strong Entity)
CREATE TABLE IF NOT EXISTS COMPUTE_NODE (
    node_id INT PRIMARY KEY AUTO_INCREMENT,
    hostname VARCHAR(100) NOT NULL UNIQUE,
    ip_address VARCHAR(45) NOT NULL,
    cpu_architecture VARCHAR(50) NOT NULL,
    os_name VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. BASELINE_PATTERN (Strong Entity - Golden Reference Profiles)
CREATE TABLE IF NOT EXISTS BASELINE_PATTERN (
    baseline_id INT PRIMARY KEY AUTO_INCREMENT,
    pattern_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    expected_ipc DECIMAL(5,2) NOT NULL,
    expected_cache_miss_rate DECIMAL(5,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. ALGORITHM (Child of DEVELOPER + Self-Referencing Recursive Lineage)
CREATE TABLE IF NOT EXISTS ALGORITHM (
    algo_id INT PRIMARY KEY AUTO_INCREMENT,
    dev_id INT NOT NULL,
    algo_name VARCHAR(100) NOT NULL,
    language VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    parent_algo_id INT NULL,
    FOREIGN KEY (dev_id) REFERENCES DEVELOPER(dev_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_algo_id) REFERENCES ALGORITHM(algo_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. EXECUTION_RUN (Child of ALGORITHM & COMPUTE_NODE)
CREATE TABLE IF NOT EXISTS EXECUTION_RUN (
    run_id INT PRIMARY KEY AUTO_INCREMENT,
    algo_id INT NOT NULL,
    node_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NULL,
    execution_status VARCHAR(30) NOT NULL,
    peak_memory_mb DECIMAL(10,2) NULL,
    FOREIGN KEY (algo_id) REFERENCES ALGORITHM(algo_id) ON DELETE CASCADE,
    FOREIGN KEY (node_id) REFERENCES COMPUTE_NODE(node_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. FINGERPRINT (Strict 1:1 Child of EXECUTION_RUN)
-- run_id is UNIQUE to guarantee strict 1:1 cardinality
CREATE TABLE IF NOT EXISTS FINGERPRINT (
    fingerprint_id INT PRIMARY KEY AUTO_INCREMENT,
    run_id INT NOT NULL UNIQUE,
    ipc_ratio DECIMAL(6,3) NOT NULL,
    cache_miss_rate DECIMAL(5,2) NOT NULL,
    branch_misprediction_rate DECIMAL(5,2) NOT NULL,
    signature_hash VARCHAR(64) NOT NULL UNIQUE,
    FOREIGN KEY (run_id) REFERENCES EXECUTION_RUN(run_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. DETECTION_LOG (Junction Entity: FINGERPRINT <-> BASELINE_PATTERN)
CREATE TABLE IF NOT EXISTS DETECTION_LOG (
    detection_id INT PRIMARY KEY AUTO_INCREMENT,
    fingerprint_id INT NOT NULL,
    baseline_id INT NOT NULL,
    similarity_score DECIMAL(5,2) NOT NULL,
    alert_level VARCHAR(20) NOT NULL,
    classification_result VARCHAR(50) NOT NULL,
    FOREIGN KEY (fingerprint_id) REFERENCES FINGERPRINT(fingerprint_id) ON DELETE CASCADE,
    FOREIGN KEY (baseline_id) REFERENCES BASELINE_PATTERN(baseline_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ====================================================================
-- DATABASE ROLE-BASED ACCESS CONTROL (RBAC)
-- ====================================================================

-- Create Roles
CREATE ROLE IF NOT EXISTS 'sec_admin', 'sec_analyst';

-- Grant Privileges
GRANT ALL PRIVILEGES ON algo_fingerprint_db.* TO 'sec_admin' WITH GRANT OPTION;

GRANT SELECT ON algo_fingerprint_db.* TO 'sec_analyst';
GRANT INSERT ON algo_fingerprint_db.execution_run TO 'sec_analyst';
GRANT INSERT ON algo_fingerprint_db.fingerprint TO 'sec_analyst';
GRANT INSERT ON algo_fingerprint_db.detection_log TO 'sec_analyst';

-- Create User Accounts
CREATE USER IF NOT EXISTS 'admin_user'@'localhost' IDENTIFIED BY 'Admin@Sec2026!';
CREATE USER IF NOT EXISTS 'analyst_user'@'localhost' IDENTIFIED BY 'Analyst@Sec2026!';

GRANT 'sec_admin' TO 'admin_user'@'localhost';
GRANT 'sec_analyst' TO 'analyst_user'@'localhost';

SET DEFAULT ROLE 'sec_admin' TO 'admin_user'@'localhost';
SET DEFAULT ROLE 'sec_analyst' TO 'analyst_user'@'localhost';

FLUSH PRIVILEGES;
