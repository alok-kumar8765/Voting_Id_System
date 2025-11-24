import requests

FASTAPI_URL = "http://127.0.0.1:8001"

def register_face(voter_id, file_path):
    with open(file_path, "rb") as f:
        files = {"file": f}
        resp = requests.post(f"{FASTAPI_URL}/register_face/", data={"voter_id": voter_id}, files=files)
        return resp.json()

def check_duplicate(file_path):
    with open(file_path, "rb") as f:
        files = {"file": f}
        resp = requests.post(f"{FASTAPI_URL}/check_duplicate/", files=files)
        return resp.json()
