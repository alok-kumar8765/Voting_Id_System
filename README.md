# Voting_Id_System
Using Django and FastAPI for simple voting system.

🟦 Step 1 — Install Python & Virtual Environment

	1. Install Python 3.11+
		Check version:

		python --version


	2. Create a virtual environment:

		mkdir voter_system
		cd voter_system
		python -m venv venv


	3. Activate the virtual environment:

		Windows:

			venv\Scripts\activate


		Mac/Linux:

			source venv/bin/activate


	4. Upgrade pip:

		pip install --upgrade pip

🟦 Step 2 — Install Django + FastAPI + Required Packages

	# Django core
	pip install django psycopg2-binary djangorestframework

	# FastAPI for AI microservice
	pip install fastapi uvicorn[standard] python-multipart pydantic aiofiles
	
	# Install FastAPI & Uvicorn for ML service
	pip install fastapi uvicorn python-multipart pillow opencv-python numpy face-recognition scikit-learn

	# ML packages (Face/Signature)
	pip install opencv-python face_recognition numpy pillow scikit-learn tensorflow torch torchvision

	# PDF generator
	pip install weasyprint reportlab fpdf2

	# Optional: language support for Hindi
	pip install babel

🟦 Step 3 — Django Project Setup

	1. Create Django project:
	
		django-admin startproject voter_project
		cd voter_project
		python manage.py startapp voters

	Your structure now:
	
		voter_system/
		├─ venv/
		├─ voter_project/
		│  ├─ voter_project/
		│  │  ├─ settings.py
		│  │  ├─ urls.py
		│  │  └─ wsgi.py
		│  └─ voters/
		│     ├─ models.py
		│     ├─ views.py
		│     └─ admin.py


	2. Add apps to settings.py:
	
		INSTALLED_APPS = [
		'django.contrib.admin',
		'django.contrib.auth',
		'django.contrib.contenttypes',
		'django.contrib.sessions',
		'django.contrib.messages',
		'django.contrib.staticfiles',
		'rest_framework',  # Django REST Framework
		'voters',          # Your voter app
	]

	3. Setup database (SQLite for local testing):
	
		DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.sqlite3',
			'NAME': BASE_DIR / "db.sqlite3",
			}
		}
	
	4 — Run FastAPI Microservice
	cd fastapi_service
	uvicorn main:app --reload --port 8001

	Test via browser or Postman:
		http://127.0.0.1:8001/docs
	
	Test ML APIs:
		http://127.0.0.1:8001/docs

# Architecture Diagram 
              ┌─────────────────────────────┐
              │        Frontend (Web)       │
              │ HTML / Bootstrap / JS       │
              └─────────────┬──────────────┘
                            │
                            │ HTTP / REST API
                            ▼
              ┌─────────────────────────────┐
              │        Django Backend       │
              │ - Voter CRUD (DRF)         │
              │ - Admin Panel              │
              │ - PDF Generation           │
              │ - Logging                  │
              └─────────────┬──────────────┘
                            │
                            │ ML API Calls (HTTP)
                            ▼
              ┌─────────────────────────────┐
              │      FastAPI ML Service     │
              │ - Face Recognition          │
              │ - Signature Matching        │
              │ - Duplicate Detection       │
              └─────────────┬──────────────┘
                            │
                            │ Returns JSON
                            ▼
              ┌─────────────────────────────┐
              │     Voter Database (SQL)    │
              │ - States                    │
              │ - Constituencies            │
              │ - Booths                    │
              │ - Voters                    │
              │ - AdminLog                  │
              │ - DuplicateLog              │
              └─────────────────────────────┘

# 🗳️ **Voter ID Management System (MySQL + SQL Utilities)**  
A complete SQL-powered voter database system for **generating**, **cleaning**, **searching**, **detecting duplicates**, **logging**, and **analyzing** voter data.  
Includes **100+ MySQL operations**, dummy data generator, soft delete logic, analytics, fraud detection & more.

---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output1.png" width="85%">
</p>

---

# 📚 **Table of Contents**
- [✨ Features](#-features)
- [🛠️ Database Structure](#️-database-structure)
- [🚀 Dummy Data Generator](#-dummy-data-generator)
- [🧹 Data Cleanup Queries](#-data-cleanup-queries)
- [📌 Searching + Filtering](#-searching--filtering)
- [📊 Analytics & Reports](#-analytics--reports)
- [🔄 Duplicate Detection & Merge](#-duplicate-detection--merge)
- [🛡️ Fraud Detection (Multi-State)](#️-fraud-detection-multi-state)
- [📝 Logs & Admin Actions](#-logs--admin-actions)
- [📤 Export Queries](#-export-queries)
- [💡 Future Enhancements](#-future-enhancements)
- [📷 Screenshots](#-screenshots)

---

# ✨ **Features**
✔️ Auto-generate dummy voters  
✔️ Automatic EPIC + unique codes  
✔️ Add-on utilities: age calculation, DOB fix, status randomizer  
✔️ Advanced filtering (phone, name, age range, gender, state, constituency)  
✔️ Fraud detection (same person in multiple states)  
✔️ Duplicate voter detection (name, phone, address, fingerprint)  
✔️ Soft delete + full log tracking  
✔️ State-wise & constituency analytics  
✔️ CSV export support  

---

# 🛠️ **Database Structure**

### **Main Tables**
| Table | Purpose |
|-------|---------|
| **Voters** | Stores all voter details |
| **States** | List of states |
| **Constituencies** | Constituency details |
| **VoterLogs** | Audit log for voter updates/deletes |
| **AdminLogs** | Admin tracking |
| **BiometricData** | Fingerprint / photo hashes |

---
# 🚀 **Dummy Data Generator**
Automatically inserts **600+ random voters** with:

- Random state & constituency  
- Auto EPIC numbers  
- Random names, relations  
- Fake addresses  
- Random DOB  
- Auto age calculation  
- Gender & phone  

---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output2.png" width="85%">
</p>

---
# 🧹 **Data Cleanup Queries**

- Replace fake names (`User_*`)  
- Fix relation (Father/Mother/Husband/Wife)  
- Add `age` column automatically  
- Recalculate age for any year  
- Randomize status (`active/inactive/migrated/deleted`)  

---

# 🧹 **Insert Data Queries**

```sql
/* ===============================================================
   1. INSERT DUMMY VOTERS
   =============================================================== */

CREATE TEMPORARY TABLE NameList (name VARCHAR(50));
INSERT INTO NameList VALUES
('Rahul'),('Raj'),('Amit'),('Vikram'),('Suresh'),
('Ramesh'),('Anil'),('Arjun'),('Manish'),('Gaurav'),
('Priya'),('Pooja'),('Sneha'),('Ananya'),('Kavita'),
('Ritu'),('Neha'),('Shweta'),('Divya'),('Nisha');

INSERT INTO Voters (
    state_id, constituency_id, epic_number, unique_code,
    name, relation_type, relation_name,
    address, phone, date_of_birth, gender
)
SELECT
    FLOOR(1 + RAND()*6),
    FLOOR(1 + RAND()*12),
    CONCAT('XX', LPAD(FLOOR(RAND()*9999999999), 10,'0')),
    LPAD(FLOOR(RAND()*9999), 4, '0'),
    (SELECT name FROM NameList ORDER BY RAND() LIMIT 1),
    ELT(FLOOR(1 + RAND()*4), 'Father','Mother','Husband','Wife'),
    CONCAT('Relative_', FLOOR(RAND()*5000)),
    CONCAT('House No ', FLOOR(RAND()*200)+1, ', Street ', FLOOR(RAND()*50)+1),
    CONCAT('9', FLOOR(RAND()*999999999)),
    DATE_SUB(CURDATE(), INTERVAL FLOOR(RAND()*25000) DAY),
    ELT(FLOOR(1 + RAND()*3), 'Male','Female','Other')
FROM
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) A,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) B;


/* ===============================================================
   2. CLEANUP / FIX DATA
   =============================================================== */

-- replace User_*****
UPDATE Voters
SET name = (SELECT name FROM NameList ORDER BY RAND() LIMIT 1)
WHERE name LIKE 'User_%';

-- fix relation names
UPDATE Voters
SET relation_name =
    CASE relation_type
        WHEN 'Father' THEN CONCAT('Mr. ', name, ' Sr.')
        WHEN 'Mother' THEN CONCAT('Mrs. ', name, ' Sr.')
        WHEN 'Husband' THEN CONCAT('Mr. ', name, ' Spouse')
        WHEN 'Wife' THEN CONCAT('Mrs. ', name, ' Spouse')
        ELSE relation_name
    END;

-- randomize status
UPDATE Voters
SET status = ELT(FLOOR(1 + RAND()*4), 'active','inactive','migrated','deleted');


/* ===============================================================
   3. ADD AGE COLUMN (Safe for all MySQL versions)
   =============================================================== */

SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE table_name='Voters' 
      AND column_name='age' 
      AND table_schema=DATABASE()
);

SET @s = IF(@col_exists=0,'ALTER TABLE Voters ADD COLUMN age INT','SELECT "Column exists"');
PREPARE stmt FROM @s;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- update age as of 2025
UPDATE Voters
SET age = TIMESTAMPDIFF(YEAR, date_of_birth, '2025-01-01');


/* ===============================================================
   4. FINAL OUTPUT
   =============================================================== */

SELECT voter_id, name, age, state_id, constituency_id, relation_type, relation_name, status
FROM Voters
LIMIT 20;
```
---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output1.png" width="85%">
</p>

---

## Using Join
```sql
SELECT 
    v.voter_id,
    v.name,
    v.age,
    s.state_name,
    c.constituency_name,
    v.relation_type,
    v.relation_name,
    v.status
FROM Voters v
LEFT JOIN States s ON v.state_id = s.state_id
LEFT JOIN Constituencies c ON v.constituency_id = c.constituency_id
LIMIT 20;

```

---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output2.png" width="85%">
</p>

---

## 🔍 1. Search by Partial Phone Number
```sql
SELECT * FROM Voters
WHERE phone = '9716179463';

		/* or */

SELECT * FROM Voters
WHERE phone = '9876543210' AND name LIKE '%Amit%';

```

## 🔍 2. Search by Age Range
```sql
SELECT 
    name, 
    TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age
FROM Voters
WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) BETWEEN 18 AND 25;

```

---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output3.png" width="85%">
</p>

---

## 🔍 3. Search by Gender + Constituency
```sql
SELECT v.*
FROM Voters v
WHERE v.gender = 'Female'
  AND v.constituency_id = 2;
```

---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output4.png" width="85%">
</p>

---

## 🔍 4. Count Underage Voters (<18) & Details
```sql
SELECT COUNT(*) AS underage_voters
FROM Voters
WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 18;


SELECT 
    voter_id,
    name,
    date_of_birth,
    TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age,
    state_id,
    constituency_id,
    relation_type,
    relation_name,
    phone,
    status
FROM Voters
WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 18;

```
---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output5.png" width="85%">
</p>

---

## 🔍 5. List All Active Voters with Relations
```sql
SELECT 
    voter_id, name, relation_type, relation_name, phone
FROM Voters
WHERE status = 'active';
```


---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output6.png" width="85%">
</p>

---

## 🔍 6. Show Voters With No Phone
```sql
SELECT * FROM Voters WHERE phone = '' OR phone IS NULL;
```

## 🔍 7. List Voters by State Name
```sql
SELECT v.*, s.state_name
FROM Voters v
JOIN States s ON v.state_id = s.state_id
WHERE s.state_name = 'Uttar Pradesh';

```

---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output7.png" width="85%">
</p>

---

## 🔍 8. Newly Added Voters (Last 7 Days)
```sql
SELECT * FROM Voters
WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);

```
---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output8.png" width="85%">
</p>

---

## 🔍 9. Log Every Update to a Voter
```sql
INSERT INTO VoterLogs (voter_id, action, admin_id, comments)
VALUES (10, 'updated', 101, 'Updated phone number');

```

## 🔍 10. Show Activity Logs by Admin
```sql
SELECT * FROM AdminLogs ORDER BY action_date DESC;

```

## Duplicate Detection by Phone
```sql
SELECT name, COUNT(*) AS cnt
FROM Voters
GROUP BY name
HAVING cnt > 1;

```
---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output9.png" width="85%">
</p>

---

## 11. Calculate Age in a Given Year
```sql
SELECT 
    name, 
    GetAgeOnYear(date_of_birth, 2025) AS age_in_2025
FROM Voters;

```

---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output10.png" width="85%">
</p>

---

## 12. Search via unique code
```sql
SELECT * FROM Voters WHERE unique_code = '1234';

```

## 13. Search via EPIC number
```sql
SELECT * FROM Voters WHERE epic_number = 'UK1234567890';

```

## 14. Maximum and minimum voters per State

### **-- State with maximum voters**
```sql
SELECT s.state_name, COUNT(v.voter_id) AS total_voters
FROM Voters v
JOIN States s ON v.state_id = s.state_id
GROUP BY s.state_id
ORDER BY total_voters DESC
LIMIT 1;
```
### **-- State with minimum voters**
```sql
SELECT s.state_name, COUNT(v.voter_id) AS total_voters
FROM Voters v
JOIN States s ON v.state_id = s.state_id
GROUP BY s.state_id
ORDER BY total_voters ASC
LIMIT 1;
```


---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output11.png" width="85%">
</p>

---

## 15. Maximum and minimum voters per Constituency

###  **-- Constituency with maximum voters**
```sql
SELECT c.constituency_name, COUNT(v.voter_id) AS total_voters
FROM Voters v
JOIN Constituencies c ON v.constituency_id = c.constituency_id
GROUP BY c.constituency_id
ORDER BY total_voters DESC
LIMIT 1;
```
### **-- Constituency with minimum voters**
```sql
SELECT c.constituency_name, COUNT(v.voter_id) AS total_voters
FROM Voters v
JOIN Constituencies c ON v.constituency_id = c.constituency_id
GROUP BY c.constituency_id
ORDER BY total_voters ASC
LIMIT 1;

```
---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output12.png" width="85%">
</p>

---

---
# 📊 **Analytics & Reports**

### ✔ State with maximum voters  
### ✔ State with minimum voters  
### ✔ Constituency with highest population  
### ✔ Underage voters (<18)  
### ✔ Senior voters (>100)  
### ✔ Only active voters  
### ✔ Voter creation trend (last 7 days)  

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output11.png" width="78%">
</p>

---
## 16. Find Underage (<18) Voters
```sql
SELECT voter_id, name, date_of_birth,
       TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age
FROM Voters
WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 18;

```

## 17. Find Senior (>100) Voters
```sql
SELECT voter_id, name, date_of_birth,
       TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age
FROM Voters
WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) > 100;
```

## 18. Soft Delete Under-18 Voters
```sql
UPDATE Voters
SET status = 'inactive'
WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 18;
```

## 19. Soft Delete Above-100 Voters
```sql
UPDATE Voters
SET status = 'deleted'
WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) > 100;

```

## 20.  Log Soft Deleted Voters (>100)
```sql
INSERT INTO VoterLogs (voter_id, action, admin_id, comments)
SELECT voter_id, 'deleted', 1, 'Age > 100 years'
FROM Voters
WHERE status = 'deleted';
```

## 21. Find Duplicate Voters (By Name + Address)
```sql
SELECT 
    v1.voter_id AS voter1,
    v2.voter_id AS voter2,
    v1.name,
    v1.address
FROM Voters v1
JOIN Voters v2
  ON v1.name = v2.name
 AND v1.address = v2.address
 AND v1.voter_id < v2.voter_id;

```

## 22. Soft Delete Duplicate Voters
```sql
UPDATE Voters v1
JOIN Voters v2
    ON v1.name = v2.name
   AND v1.address = v2.address
   AND v1.voter_id > v2.voter_id
SET v1.status = 'deleted';

```

## 23. Show Only Active Voters
```sql
SELECT * FROM Voters
WHERE status = 'active';

```
---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output13.png" width="85%">
</p>

---

# Mysql Queries
## -------------------------------------------------------------------
## 📌 1. BASIC SELECT + SORTING + PAGINATION
## ------------------------------------------------------------------

##	**Sort by Name**
```sql
SELECT * FROM Voters ORDER BY name ASC;
```

## **Sort by Age**
```sql
SELECT * FROM Voters ORDER BY age DESC;
```

## **sqlSort by Creation Date (New to Old)**
```
SELECT * FROM Voters ORDER BY created_at DESC;
```

## **Pagination (page 2, limit 20)**
```sql
SELECT * FROM Voters LIMIT 20 OFFSET 20;
```

## -------------------------------------------------------------------
## 📌 2. BASIC SEARCHING
## -------------------------------------------------------------------

## *Search by Full or Partial Name*
```sql
SELECT * FROM Voters WHERE name LIKE '%rahul%';
```

## *Search by Phone*
```sql
SELECT * FROM Voters WHERE phone = '123456789';
```
## *Search by Partial Phone*
```sql
SELECT * FROM Voters WHERE phone LIKE '%789%';
```
## *Search by Gender*
```sql
SELECT * FROM Voters WHERE gender = 'Male';
```

## -------------------------------------------------------------------
## 📌 3. ADVANCED SEARCHING (Multiple Filters)
## -------------------------------------------------------------------

### ***Search by Name + Phone + Relation + State + Constituency***

```sql
SELECT v.*, s.state_name, c.constituency_name
FROM Voters v
JOIN States s ON v.state_id = s.state_id
JOIN Constituencies c ON v.constituency_id = c.constituency_id
WHERE v.name = 'Rahul'
  AND v.phone = '123456789'
  AND v.relation_name = 'Mohan'
  AND s.state_name = 'Delhi'
  AND c.constituency_name = 'Rohini'
  AND v.address LIKE '%House No 5%';
```

### **Search by Date Range (Created At)**

```sql
SELECT * FROM Voters
WHERE created_at BETWEEN '2025-01-01' AND '2025-02-01';
```

## -------------------------------------------------------------------
## 📌 4. AGE-BASED FILTERS
## -------------------------------------------------------------------

### **Voters Below 18**

```sql
SELECT * FROM Voters
WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 18;
```

### **Voters Above 100**

```sql
SELECT * FROM Voters
WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) > 100;
```

### **Age on a Specific Year**

```sql
SELECT name, GetAgeOnYear(date_of_birth, 2030) AS age_in_2030
FROM Voters;
```

## -------------------------------------------------------------------
## 📌 5. SOFT & HARD DELETE
## -------------------------------------------------------------------

### **Soft Delete (<18 years)**

```sql
UPDATE Voters
SET status = 'inactive'
WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 18;
```

### **Soft Delete (>100 years)**

```sql
UPDATE Voters
SET status = 'deleted'
WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) > 100;
```

### **Hard Delete**

```sql
DELETE FROM Voters WHERE voter_id = 10;
```

### **Log Soft Delete**

```sql
INSERT INTO VoterLogs(voter_id, action, admin_id, comments)
VALUES (10, 'deleted', 1, 'Soft deleted due to age rule');
```
---

# 🛡️ **Fraud Detection (Multi-State)**

Detect voters registered in **multiple states** using:

- Name  
- Phone  
- Father/Husband name  
- Biometric fingerprint match  

This can identify **cross-state voter fraud**.

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output15.png" width="80%">
</p>

---

## -------------------------------------------------------------------
## 📌 6. MULTIPLE EPIC NO. PROBLEMS
## -------------------------------------------------------------------

### **Find Voter Names Having Multiple EPIC Numbers**

```sql
SELECT name, COUNT(epic_number) AS epic_count
FROM Voters
GROUP BY name
HAVING epic_count > 1;
```
---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output14.png" width="85%">
</p>

---

### **Find Multiple EPIC for Same Phone**

```sql
SELECT phone, COUNT(epic_number) AS epic_count
FROM Voters
GROUP BY phone
HAVING epic_count > 1;
```

### **Detailed Multi-EPIC List**
```sql
SELECT v.*
FROM Voters v
JOIN (
    SELECT phone
    FROM Voters
    GROUP BY phone
    HAVING COUNT(epic_number) > 1
) d ON d.phone = v.phone;
```

## -------------------------------------------------------------------
## 📌 7. FIND DUPLICATE VOTERS (Strong)
##  -------------------------------------------------------------------

## **A. Duplicate by Name + Phone**

```sql
SELECT name, phone, COUNT(*) 
FROM Voters
GROUP BY name, phone
HAVING COUNT(*) > 1;
```
---

<p align="center">
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main/images/output15.png" width="85%">
</p>

---

## **B. Duplicate by Name + Address**

```sql
SELECT name, address, COUNT(*)
FROM Voters
GROUP BY name, address
HAVING COUNT(*) > 1;
```
## **C. Duplicate by Photograph (Biometric Table)**

### **(Assuming fingerprint hash or photo hash exists)**

```sql
SELECT b.fingerprint_data, COUNT(*)
FROM BiometricData b
GROUP BY b.fingerprint_data
HAVING COUNT(*) > 1;
```

## **D. 99% Accurate Duplicate (Multi-Factor)**

## **Same Name + Same Photo + Same Father Name (BUT DIFFERENT STATE)**

```sql
SELECT 
   v1.voter_id AS voter_in_state1,
   v2.voter_id AS voter_in_state2,
   v1.name,
   v1.relation_name AS father1,
   v2.relation_name AS father2,
   v1.address AS address1,
   v2.address AS address2,
   s1.state_name AS state1,
   s2.state_name AS state2
FROM Voters v1
JOIN Voters v2
  ON v1.name = v2.name
 AND v1.phone = v2.phone
 AND v1.voter_id < v2.voter_id
JOIN States s1 ON v1.state_id = s1.state_id
JOIN States s2 ON v2.state_id = s2.state_id
JOIN BiometricData b1 ON b1.voter_id = v1.voter_id
JOIN BiometricData b2 ON b2.voter_id = v2.voter_id
WHERE b1.fingerprint_data = b2.fingerprint_data;
```

## -------------------------------------------------------------------
## 📌 8. MERGING DUPLICATE VOTERS
## -------------------------------------------------------------------

```sql
Mark Duplicate as Deleted
UPDATE Voters v1
JOIN Voters v2
  ON v1.name = v2.name
 AND v1.phone = v2.phone
 AND v1.voter_id > v2.voter_id
SET v1.status = 'deleted';
```
### **Log All Merged Voters**
```sql
INSERT INTO VoterLogs(voter_id, action, admin_id, comments)
SELECT v1.voter_id, 'deleted', 1, 'Merged duplicate voter'
FROM Voters v1
JOIN Voters v2
  ON v1.name = v2.name
 AND v1.phone = v2.phone
 AND v1.voter_id > v2.voter_id;
```
---

# 💡 **Future Enhancements**
✔ REST API using Node.js / SpringBoot / Laravel  
✔ React/Next.js-based voter dashboard  
✔ Aadhaar + FaceID verification integration  
✔ QR-based EPIC ID generation  
✔ Bulk CSV/Excel import  
✔ Role-based admin panel  

---
## -------------------------------------------------------------------
## 📌 9. DOWNLOAD / EXPORT QUERIES
## -------------------------------------------------------------------


### **Export All Active Voters**

```sql
SELECT voter_id, name, phone, date_of_birth, epic_number
FROM Voters
WHERE status = 'active';
```

### **Export as CSV (MySQL Server Path)**

```sql
SELECT * 
INTO OUTFILE '/var/lib/mysql-files/active_voters.csv'
FIELDS TERMINATED BY ','
FROM Voters
WHERE status = 'active';
```

## -------------------------------------------------------------------
## 📌 10. ADMIN ACTIVITY QUERIES
## -------------------------------------------------------------------

## **All Admin Actions**
```sql
SELECT * FROM AdminLogs ORDER BY action_date DESC;
```

## **Actions by Specific Admin**
```sql
SELECT * FROM AdminLogs WHERE admin_id = 1;
```

## -------------------------------------------------------------------
## 📌 11. STATE / CONSTITUENCY ANALYTICS
## -------------------------------------------------------------------


### **Total Voters per State**
```sql
SELECT s.state_name, COUNT(v.voter_id) AS voters
FROM Voters v
JOIN States s ON s.state_id = v.state_id
GROUP BY s.state_name;
```

### **Max Voter State**
```sql
SELECT s.state_name, COUNT(v.voter_id) AS voters
FROM Voters v JOIN States s ON v.state_id=s.state_id
GROUP BY s.state_id
ORDER BY voters DESC LIMIT 1;
```

### **Min Voter State**
```sql
ORDER BY voters ASC LIMIT 1;
```

## -------------------------------------------------------------------
## 📌 12. VOTER FOUND IN TWO STATES (Cross-State Fraud)
## -------------------------------------------------------------------


### **Same Voter Found in Delhi + Bihar (Example Rahul)**

### ***(Uses Name + Phone + Father Name + Photo)***
```sql
SELECT 
    v1.voter_id AS id_delhi,
    v2.voter_id AS id_bihar,
    v1.name,
    v1.phone,
    v1.relation_name AS father_name,
    s1.state_name AS state1,
    s2.state_name AS state2,
    c1.constituency_name AS const1,
    c2.constituency_name AS const2
FROM Voters v1
JOIN Voters v2
  ON v1.name = v2.name
 AND v1.phone = v2.phone
 AND v1.voter_id < v2.voter_id
JOIN States s1 ON v1.state_id = s1.state_id
JOIN States s2 ON v2.state_id = s2.state_id
JOIN Constituencies c1 ON v1.constituency_id = c1.constituency_id
JOIN Constituencies c2 ON v2.constituency_id = c2.constituency_id
JOIN BiometricData b1 ON b1.voter_id = v1.voter_id
JOIN BiometricData b2 ON b2.voter_id = v2.voter_id
WHERE b1.fingerprint_data = b2.fingerprint_data;
```

---

# 💡 **Future Enhancements**
✔ REST API using Node.js / SpringBoot / Laravel  
✔ React/Next.js-based voter dashboard  
✔ Aadhaar + FaceID verification integration  
✔ QR-based EPIC ID generation  
✔ Bulk CSV/Excel import  
✔ Role-based admin panel  

---
# 📷 **Screenshots**

| Output | Image |
|--------|--------|
| Voter List | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output1.png) |
| Joined Data | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output2.png) |
| Age Filter | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output3.png) |
| Gender Filter | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output4.png) |
| Underage Voters | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output5.png) |
| Active Voters | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output6.png) |
| State Filter | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output7.png) |
| Recently Added | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output8.png) |
| Duplicate Names | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output9.png) |
| Age in 2025 | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output10.png) |
| Max/Min State | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output11.png) |
| Max/Min Constituency | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output12.png) |
| Final Active | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output13.png) |
| Multi-EPIC | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output14.png) |
| Duplicate (Name+Phone) | ![](https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/output15.png) |

---
<p align="center">

  <!-- 🔥 Your Banner Image -->
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/banner.jpg" width="900" />

  <br><br>

  <!-- 🪪 Your Logo Image -->
  <img src="https://github.com/alok-kumar8765/Voter_Id_System/blob/main//images/logo.png" width="140" />

  <br><br>

  <!-- ⭐ Badges -->
  <a href="https://www.mysql.com/">
    <img src="https://img.shields.io/badge/Database-MySQL-blue?style=for-the-badge&logo=mysql&logoColor=white" />
  </a>

  <img src="https://img.shields.io/github/stars/alok-kumar8765/Voter_Id_System?style=for-the-badge" />

  <img src="https://img.shields.io/github/forks/alok-kumar8765/Voter_Id_System?style=for-the-badge" />

  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />

  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" />

</p>
---

---

# ⭐ **Support This Project**
If this project helped you, please **⭐ Star this repository**.  
Your support encourages more updates & improvements!

---

# 🎉 Thank You!
