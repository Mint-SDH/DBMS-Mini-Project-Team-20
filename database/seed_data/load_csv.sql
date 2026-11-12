-- ====================================================================
-- LOAD DATA INFILE SCRIPT FOR algo_fingerprint_db
-- Run with MySQL local infile enabled:
-- mysql --local-infile=1 -u root -p algo_fingerprint_db < load_csv.sql
-- ====================================================================

USE algo_fingerprint_db;

SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;

-- 1. DEVELOPER
LOAD DATA LOCAL INFILE 'csv_data/developer.csv'
INTO TABLE DEVELOPER
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(dev_id, name, email, team);

-- 2. COMPUTE_NODE
LOAD DATA LOCAL INFILE 'csv_data/compute_node.csv'
INTO TABLE COMPUTE_NODE
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(node_id, hostname, ip_address, cpu_architecture, os_name);

-- 3. BASELINE_PATTERN
LOAD DATA LOCAL INFILE 'csv_data/baseline_pattern.csv'
INTO TABLE BASELINE_PATTERN
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(baseline_id, pattern_name, category, expected_ipc, expected_cache_miss_rate);

-- 4. ALGORITHM
LOAD DATA LOCAL INFILE 'csv_data/algorithm.csv'
INTO TABLE ALGORITHM
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(algo_id, dev_id, algo_name, language, version);

-- 5. EXECUTION_RUN
LOAD DATA LOCAL INFILE 'csv_data/execution_run.csv'
INTO TABLE EXECUTION_RUN
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(run_id, algo_id, node_id, start_time, @end_time, execution_status, peak_memory_mb)
SET end_time = NULLIF(@end_time, '\\N');

-- 6. FINGERPRINT
LOAD DATA LOCAL INFILE 'csv_data/fingerprint.csv'
INTO TABLE FINGERPRINT
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(fingerprint_id, run_id, ipc_ratio, cache_miss_rate, branch_misprediction_rate, signature_hash);

-- 7. DETECTION_LOG
LOAD DATA LOCAL INFILE 'csv_data/detection_log.csv'
INTO TABLE DETECTION_LOG
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(detection_id, fingerprint_id, baseline_id, similarity_score, alert_level, classification_result);

SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
