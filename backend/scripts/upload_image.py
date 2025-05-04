import requests

# Replace with your image path
image_path = "images/raw/20250420_184647_40722e28-1aa1-4424-be7b-2a4144432143.png"

with open(image_path, "rb") as img_file:
    files = {"file": img_file}
    response = requests.post("http://localhost:8000/flip/", files=files)

if response.status_code == 200:
    task_id = response.json().get("task_id")
    print(f"Image uploaded. Task ID: {task_id}")
else:
    print(f"Failed to upload image: {response.status_code}")
