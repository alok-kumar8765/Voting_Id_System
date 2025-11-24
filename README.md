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