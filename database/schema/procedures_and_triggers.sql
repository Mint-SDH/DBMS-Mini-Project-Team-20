-- ====================================================================
-- ALGORITHMIC EXECUTION FINGERPRINTING & RUNTIME THREAT DETECTION
-- Stored Procedures, Deterministic Functions, Triggers & Relational Views
-- Author: Sanyam Deven Hiran (PES2UG24CS446) | Group 20
-- Engine: MySQL 8.0+
-- Database: algo_fingerprint_db
-- ====================================================================

USE algo_fingerprint_db;

-- 1. STORED PROCEDURE: GetRunFingerprintProfile
DROP PROCEDURE IF EXISTS GetRunFingerprintProfile;
DELIMITER //
CREATE PROCEDURE GetRunFingerprintProfile(IN p_run_id INT)
BEGIN
    SELECT 
        er.run_id,
        a.algo_name,
        a.language,
        d.name AS developer_name,
        cn.hostname,
        er.start_time,
        er.end_time,
        er.peak_memory_mb,
        fp.ipc_ratio,
        fp.cache_miss_rate,
        fp.branch_misprediction_rate,
        bp.pattern_name AS matched_pattern,
        dl.similarity_score,
        dl.alert_level,
        dl.classification_result
    FROM execution_run er
    JOIN algorithm a ON er.algo_id = a.algo_id
    JOIN developer d ON a.dev_id = d.dev_id
    JOIN compute_node cn ON er.node_id = cn.node_id
    LEFT JOIN fingerprint fp ON er.run_id = fp.run_id
    LEFT JOIN detection_log dl ON fp.fingerprint_id = dl.fingerprint_id
    LEFT JOIN baseline_pattern bp ON dl.baseline_id = bp.baseline_id
    WHERE er.run_id = p_run_id;
END //
DELIMITER ;

-- 2. STORED FUNCTION: CalculateIPCDeviation
DROP FUNCTION IF EXISTS CalculateIPCDeviation;
DELIMITER //
CREATE FUNCTION CalculateIPCDeviation(p_fingerprint_id INT) 
RETURNS DECIMAL(6,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_measured_ipc DECIMAL(6,3);
    DECLARE v_expected_ipc DECIMAL(5,2);
    DECLARE v_deviation DECIMAL(6,2);

    SELECT fp.ipc_ratio, bp.expected_ipc
    INTO v_measured_ipc, v_expected_ipc
    FROM fingerprint fp
    JOIN detection_log dl ON fp.fingerprint_id = dl.fingerprint_id
    JOIN baseline_pattern bp ON dl.baseline_id = bp.baseline_id
    WHERE fp.fingerprint_id = p_fingerprint_id
    LIMIT 1;

    IF v_measured_ipc IS NULL OR v_expected_ipc IS NULL THEN
        RETURN NULL;
    END IF;

    SET v_deviation = ROUND((ABS(v_measured_ipc - v_expected_ipc) / v_expected_ipc) * 100, 2);
    RETURN v_deviation;
END //
DELIMITER ;

-- 3. TRIGGER 1: Telemetry Bounds Validation (BEFORE INSERT on FINGERPRINT)
DROP TRIGGER IF EXISTS trg_validate_fingerprint_bounds;
DELIMITER //
CREATE TRIGGER trg_validate_fingerprint_bounds 
BEFORE INSERT ON fingerprint 
FOR EACH ROW 
BEGIN
    IF NEW.ipc_ratio < 0.000 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Validation Error: IPC ratio cannot be negative.';
    END IF;

    IF NEW.cache_miss_rate < 0.00 OR NEW.cache_miss_rate > 100.00 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Validation Error: Cache miss rate must be between 0.00% and 100.00%.';
    END IF;
END //
DELIMITER ;

-- 4. TRIGGER 2: Automated Threat Mitigation (AFTER INSERT on DETECTION_LOG)
DROP TRIGGER IF EXISTS trg_auto_terminate_critical_threat;
DELIMITER //
CREATE TRIGGER trg_auto_terminate_critical_threat 
AFTER INSERT ON detection_log 
FOR EACH ROW 
BEGIN
    IF NEW.alert_level = 'Critical' THEN
        UPDATE execution_run
        SET execution_status = 'Terminated'
        WHERE run_id = (
            SELECT run_id 
            FROM fingerprint 
            WHERE fingerprint_id = NEW.fingerprint_id
        );
    END IF;
END //
DELIMITER ;

-- 5. RELATIONAL VIEW: Critical Security Anomalies
CREATE OR REPLACE VIEW vw_critical_security_anomalies AS
SELECT 
    dl.detection_id,
    er.run_id,
    a.algo_name,
    d.name AS developer_name,
    d.team,
    cn.hostname,
    bp.pattern_name AS detected_threat_signature,
    dl.similarity_score,
    dl.alert_level,
    dl.classification_result,
    fp.signature_hash
FROM detection_log dl
JOIN baseline_pattern bp ON dl.baseline_id = bp.baseline_id
JOIN fingerprint fp ON dl.fingerprint_id = fp.fingerprint_id
JOIN execution_run er ON fp.run_id = er.run_id
JOIN algorithm a ON er.algo_id = a.algo_id
JOIN developer d ON a.dev_id = d.dev_id
JOIN compute_node cn ON er.node_id = cn.node_id
WHERE dl.alert_level IN ('Critical', 'High');

-- Grant execute permissions to sec_analyst
GRANT EXECUTE ON PROCEDURE algo_fingerprint_db.GetRunFingerprintProfile TO 'sec_analyst';
GRANT EXECUTE ON FUNCTION algo_fingerprint_db.CalculateIPCDeviation TO 'sec_analyst';
FLUSH PRIVILEGES;
