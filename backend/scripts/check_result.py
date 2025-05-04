import requests
import time

task_id = input("Enter task ID: ")

while True:
    response = requests.get(f"http://localhost:8000/result/{task_id}")
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        break

    content_type = response.headers.get("content-type")

    if content_type == "application/json":
        status = response.json().get("status")
        print(f"Task status: {status}")
        if status == "SUCCESS":
            continue  # rare race condition
        elif status != "processing":
            print("Unexpected status.")
            break
        time.sleep(1)  # retry
    elif content_type.startswith("image/"):
        with open("flipped_result.png", "wb") as f:
            f.write(response.content)
        print("Flipped image saved as 'flipped_result.png'")
        break
    else:
        print("Unexpected response format")
        break
