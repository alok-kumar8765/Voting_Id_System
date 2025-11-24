/* ===============================================================
   RESET OLD SCHEMA (SAFE)
   =============================================================== */

DROP TABLE IF EXISTS UpdateLogs;
DROP TABLE IF EXISTS Notifications;
DROP TABLE IF EXISTS DeathRecords;
DROP TABLE IF EXISTS DuplicateCheckLog;
DROP TABLE IF EXISTS AdminLogs;
DROP TABLE IF EXISTS FamilyRelations;
DROP TABLE IF EXISTS BiometricData;
DROP TABLE IF EXISTS Voters;
DROP TABLE IF EXISTS Booths;
DROP TABLE IF EXISTS Constituencies;
DROP TABLE IF EXISTS States;
DROP TABLE IF EXISTS Localization;



/* ===============================================================
   1. STATES TABLE
   =============================================================== */

CREATE TABLE States (
    state_id INT PRIMARY KEY AUTO_INCREMENT,
    state_name VARCHAR(100) UNIQUE NOT NULL,
    epic_prefix VARCHAR(5) UNIQUE NOT NULL
);

INSERT INTO States (state_name, epic_prefix) VALUES
('Uttarakhand', 'UK'),
('Bihar', 'BH'),
('Delhi', 'DL'),
('Rajasthan', 'RJ'),
('Uttar Pradesh', 'UP'),
('Madhya Pradesh', 'MP');



/* ===============================================================
   2. CONSTITUENCIES
   =============================================================== */

CREATE TABLE Constituencies (
    constituency_id INT PRIMARY KEY AUTO_INCREMENT,
    constituency_name VARCHAR(255) NOT NULL,
    state_id INT NOT NULL,
    FOREIGN KEY (state_id) REFERENCES States(state_id)
);

INSERT INTO Constituencies (constituency_name, state_id) VALUES
('Dehradun', 1),
('Haridwar', 1),
('Patna Sahib', 2),
('Gaya', 2),
('New Delhi', 3),
('South Delhi', 3),
('Jaipur', 4),
('Kota', 4),
('Lucknow', 5),
('Varanasi', 5),
('Bhopal', 6),
('Indore', 6);



/* ===============================================================
   3. POLLING BOOTHS (NEW FEATURE C)
   =============================================================== */

CREATE TABLE Booths (
    booth_id INT PRIMARY KEY AUTO_INCREMENT,
    booth_name VARCHAR(255),
    constituency_id INT,
    max_voter_capacity INT DEFAULT 1200,
    wheelchair_access BOOLEAN DEFAULT FALSE,
    ramp_available BOOLEAN DEFAULT FALSE,
    gps_lat DECIMAL(10,7),
    gps_long DECIMAL(10,7),
    FOREIGN KEY (constituency_id) REFERENCES Constituencies(constituency_id)
);



/* ===============================================================
   4. MAIN VOTERS TABLE (WITH ALL NEW FEATURES)
   =============================================================== */

CREATE TABLE Voters (
    voter_id INT PRIMARY KEY AUTO_INCREMENT,

    state_id INT,
    constituency_id INT,
    booth_id INT,

    epic_number VARCHAR(20) UNIQUE NOT NULL,
    unique_code CHAR(4) NOT NULL,

    aadhaar_encrypted VARBINARY(255),        -- ENCRYPTED NATIONAL ID (Feature B)

    name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('Male','Female','Other') NOT NULL,

    relation_type ENUM('Father','Mother','Husband','Wife','Guardian','None') DEFAULT 'None',
    relation_name VARCHAR(255),

    address TEXT,
    phone VARCHAR(15),

    photo_url VARCHAR(255),                 -- Feature A
    signature_url VARCHAR(255),             -- Feature A

    status ENUM('active','inactive','migrated','deleted','dead') DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (state_id) REFERENCES States(state_id),
    FOREIGN KEY (constituency_id) REFERENCES Constituencies(constituency_id),
    FOREIGN KEY (booth_id) REFERENCES Booths(booth_id)
);





/* ===============================================================
   5. ADDRESSES (Permanent / Current / Previous)
   =============================================================== */

CREATE TABLE Addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    voter_id INT NOT NULL,
    type ENUM('Permanent','Current','Previous') NOT NULL,
    full_address TEXT NOT NULL,
	house_number INT(10),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voter_id) REFERENCES Voters(voter_id)
);



/* ===============================================================
   6. BIOMETRIC TABLE
   =============================================================== */

CREATE TABLE BiometricData (
    biometric_id INT PRIMARY KEY AUTO_INCREMENT,
    voter_id INT,
    fingerprint_data BLOB,
    iris_scan_data BLOB,
    FOREIGN KEY (voter_id) REFERENCES Voters(voter_id) ON DELETE CASCADE
);



/* ===============================================================
   7. FAMILY RELATIONS
   =============================================================== */

CREATE TABLE FamilyRelations (
    relation_id INT PRIMARY KEY AUTO_INCREMENT,
    voter_id INT,
    relative_name VARCHAR(255),
    relation_type ENUM('Father','Mother','Husband','Wife','Son','Daughter','Guardian'),
    FOREIGN KEY (voter_id) REFERENCES Voters(voter_id)
);



/* ===============================================================
   8. DEATH VERIFICATION (Feature G)
   =============================================================== */

CREATE TABLE DeathRecords (
    death_id INT PRIMARY KEY AUTO_INCREMENT,
    voter_id INT UNIQUE,
    death_certificate_number VARCHAR(255),
    certificate_url VARCHAR(255),
    verified_by_admin INT,
    verified_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voter_id) REFERENCES Voters(voter_id)
);



/* ===============================================================
   9. NOTIFICATION TABLE (Feature D)
   =============================================================== */

CREATE TABLE Notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    voter_id INT,
    message TEXT,
    notification_type ENUM('sms','email'),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voter_id) REFERENCES Voters(voter_id)
);



/* ===============================================================
   10. ADMIN LOGS + FIELD-LEVEL UPDATE LOGS (Feature E)
   =============================================================== */

CREATE TABLE AdminLogs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    admin_id INT,
    action VARCHAR(255),
    details TEXT,
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE UpdateLogs (
    update_id INT PRIMARY KEY AUTO_INCREMENT,
    voter_id INT,
    field_name VARCHAR(255),
    old_value TEXT,
    new_value TEXT,
    updated_by_admin INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voter_id) REFERENCES Voters(voter_id)
);



/* ===============================================================
   11. DUPLICATE CHECK (Feature F)
   =============================================================== */

CREATE TABLE DuplicateCheckLog (
    check_id INT PRIMARY KEY AUTO_INCREMENT,
    voter_id INT,
    duplicate_found BOOLEAN,
    rule_matched VARCHAR(255),
    comments TEXT,
    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voter_id) REFERENCES Voters(voter_id)
);



/* ===============================================================
   12. MULTI-LANGUAGE SUPPORT (Feature H)
   =============================================================== */

CREATE TABLE Localization (
    id INT PRIMARY KEY AUTO_INCREMENT,
    key_name VARCHAR(255),
    english_text TEXT,
    hindi_text TEXT,
    regional_text TEXT
);



/* ===============================================================
   13. AGE FUNCTION
   =============================================================== */

DELIMITER $$

CREATE FUNCTION GetAgeOnYear(dob DATE, target_year INT)
RETURNS INT
DETERMINISTIC
BEGIN
    RETURN target_year - YEAR(dob)
     - (DATE_FORMAT(dob,'%m-%d') > CONCAT(target_year,'-',DATE_FORMAT(CURDATE(),'%m-%d')));
END$$

DELIMITER ;



/* ===============================================================
   14. INSERT 1000 DUMMY VOTERS
   =============================================================== */

INSERT INTO Voters (
    state_id, constituency_id, booth_id,
    epic_number, unique_code, phone,
    name, date_of_birth, gender,
    relation_type, relation_name,
    aadhaar_encrypted,
    status
)
SELECT
    s.state_id,
    c.constituency_id,
    NULL,

    CONCAT(s.epic_prefix, LPAD(FLOOR(RAND()*9999999999), 10,'0')),

    LPAD(FLOOR(1000 + RAND()*8999), 4, '0'),

    CONCAT('9', LPAD(FLOOR(RAND()*999999999), 9, '0')),

    CONCAT('User_', FLOOR(RAND()*90000)+10000),

    DATE_SUB(CURDATE(), INTERVAL FLOOR(18 + RAND()*60) YEAR),

    ELT(FLOOR(1 + RAND()*3), 'Male','Female','Other'),

    ELT(FLOOR(1 + RAND()*5), 'Father','Mother','Husband','Wife','Guardian'),
    CONCAT('Relative_', FLOOR(RAND()*10000)),

    AES_ENCRYPT('123412341234', 'SECRET_KEY'),

    'active'
FROM States s
JOIN Constituencies c ON c.state_id = s.state_id
LIMIT 1000;



/* ===============================================================
   DISPLAY DATA
   =============================================================== */

SELECT * from Voters LIMIT 20;
SELECT name, GetAgeOnYear(date_of_birth, 2025) AS age_in_2025
FROM Voters;




/* ===============================================================
   15. STORED PROCEDURE — VIEW VOTER + AGE NOW
   =============================================================== */

DELIMITER $$

CREATE PROCEDURE GetVoterDetails(IN p_voter_id INT)
BEGIN
    SELECT 
        v.*,
        TIMESTAMPDIFF(YEAR, v.date_of_birth, CURDATE()) AS current_age
    FROM Voters v
    WHERE v.voter_id = p_voter_id;
END$$

DELIMITER ;



/* ===============================================================
   16. STORED PROCEDURE — VIEW VOTER BY YEAR (HISTORICAL AGE)
   =============================================================== */

DELIMITER $$

CREATE PROCEDURE GetVoterDetailsByYear(
    IN p_voter_id INT,
    IN p_year INT
)
BEGIN
    SELECT 
        v.*,
        GetAgeOnYear(v.date_of_birth, p_year) AS age_in_requested_year
    FROM Voters v
    WHERE v.voter_id = p_voter_id;
END$$

DELIMITER ;



/* ===============================================================
   17. ADVANCED DUPLICATE CHECK (Feature F)
   =============================================================== */

INSERT INTO DuplicateCheckLog (voter_id, duplicate_found, rule_matched, comments)
SELECT v1.voter_id, TRUE,
    CASE
        WHEN v1.name = v2.name AND v1.date_of_birth = v2.date_of_birth THEN 'Name + DOB Match'
        WHEN SOUNDEX(v1.name) = SOUNDEX(v2.name) THEN 'Soundex Match'
        WHEN v1.address = v2.address THEN 'Address Match'
        WHEN v1.relation_name = v2.relation_name THEN 'Relative Name Match'
    END,
    'Possible Duplicate'
FROM Voters v1
JOIN Voters v2
  ON v1.voter_id > v2.voter_id
 AND (
        (v1.name = v2.name AND v1.date_of_birth = v2.date_of_birth) OR
        SOUNDEX(v1.name) = SOUNDEX(v2.name) OR
        v1.address = v2.address OR
        v1.relation_name = v2.relation_name
     );



/* ============================== DONE =============================== */
