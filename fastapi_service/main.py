from fastapi import FastAPI, File, UploadFile
import numpy as np
import face_recognition
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from skimage.io import imread
from skimage.metrics import structural_similarity as ssim
import cv2
app = FastAPI(title="Voter ML Service")

# Allow requests from Django frontend
app.add_middleware( 
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"],
    )

# In-memory "database" of embeddings for demo
known_faces = {}
known_signatures = {}

@app.post("/register_face/")
async def register_face(voter_id: int, file: UploadFile = File(...)):
    img = face_recognition.load_image_file(file.file)
    encodings = face_recognition.face_encodings(img)
    if len(encodings) == 0:
        return {"error": "No face found"}
    known_faces[voter_id] = encodings[0].tolist()
    return {"status": "Face registered"}

@app.post("/check_duplicate/")
async def check_duplicate(file: UploadFile = File(...)):
    img = face_recognition.load_image_file(file.file)
    encodings = face_recognition.face_encodings(img)
    if len(encodings) == 0:
        return {"error": "No face found"}
    face_vector = encodings[0]
    duplicates = []
    for voter_id, known_vector in known_faces.items():
        distance = np.linalg.norm(np.array(known_vector) - face_vector)
        if distance < 0.6:
            duplicates.append({"voter_id": voter_id, "distance": distance})
    return {"duplicates": duplicates}

# Signature placeholder (similar logic)
@app.post("/register_signature/")
async def register_signature(voter_id:int, file: UploadFile = File(...)): 
    known_signatures[voter_id] = file.filename
    return {"status":"Signature registered"}

# for AI/ML
@app.post("/check_duplicate_signature/")
async def check_duplicate_signature(file: UploadFile = File(...)):
    img = imread(file.file)
    duplicates = []
    for voter_id, known_file in known_signatures.items():
        known_img = imread(known_file)
        # Convert to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        known_gray = cv2.cvtColor(known_img, cv2.COLOR_BGR2GRAY)
        score, _ = ssim(img_gray, known_gray, full=True)
        if score > 0.85:
            duplicates.append({"voter_id": voter_id, "similarity": score})
    return {"duplicates": duplicates}


@app.post("/check_duplicate_fingerprint/")
async def check_duplicate_fingerprint(file: UploadFile = File(...), voter_id: int = None):
    # Placeholder: compare fingerprint with known_fingerprints dict
    if voter_id in known_fingerprints:
        # simple byte comparison example
        uploaded_bytes = await file.read()
        known_bytes = known_fingerprints[voter_id]
        match = uploaded_bytes == known_bytes
        return {"match": match, "voter_id": voter_id}
    return {"match": False}


import requests
from django.views.decorators.csrf import csrf_exempt

FASTAPI_URL = "http://127.0.0.1:8001"

@csrf_exempt
def verify_voter_pdf(request, voter_id):
    """
    Step 2: Verify OTP + optional face/fingerprint
    """
    voter = Voter.objects.get(id=voter_id)
    input_otp = request.POST.get("otp")
    cached_otp = cache.get(f"voter_otp_{voter.id}")

    if str(input_otp) != str(cached_otp):
        return HttpResponse("OTP Verification Failed", status=400)

    # Optional: Face verification
    face_file = request.FILES.get("face_image")
    if face_file:
        resp = requests.post(
            f"{FASTAPI_URL}/check_duplicate_face/",
            files={"file": face_file}
        )
        data = resp.json()
        if not data.get("duplicates") or all(d["voter_id"] != voter.id for d in data["duplicates"]):
            return HttpResponse("Face verification failed", status=400)

    # Optional: Fingerprint verification
    fingerprint_file = request.FILES.get("fingerprint")
    if fingerprint_file:
        resp = requests.post(
            f"{FASTAPI_URL}/check_duplicate_fingerprint/",
            files={"file": fingerprint_file}
        )
        data = resp.json()
        if not data.get("match") or data.get("voter_id") != voter.id:
            return HttpResponse("Fingerprint verification failed", status=400)

    # OTP + biometric passed → Generate PDF
    return generate_voter_pdf(request, voter.id)


