import requests
import time

task_id = input("Enter task ID: ")

while True:
    response = requests.get(f"http://localhost:8000/result/{task_id}")
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        break

    content_type = response.headers.get("content-type")
    content = response.json()
    if content_type == "application/json":
        status = content.get("status")
        print(f"Task status: {status}")
        if status == "processed":
            file_path = content.get("file_path")
            print(f"processed image saved to {file_path}")
            break
        elif status != "processing":
            print("Unexpected status.")
            break
        time.sleep(1)  # retry

    else:
        print("Unexpected response format")
        break
