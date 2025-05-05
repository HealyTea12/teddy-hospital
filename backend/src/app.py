from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from .worker import process_image_task, celery_app
from io import BytesIO

app = FastAPI()


@app.post("/flip/")
async def flip_image(file: UploadFile = File(...)):
    image_data = await file.read()
    task = process_image_task.delay(image_data)
    return {"task_id": task.id}


@app.get("/result/{task_id}")
def get_result(task_id: str):
    result = celery_app.AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": "processing"}
    elif result.state == "SUCCESS":
        file_path = result.get()
        return {"status": "processed", "file_path": file_path}
    else:
        return {"status": result.state}
