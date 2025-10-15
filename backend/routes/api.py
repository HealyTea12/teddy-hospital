import base64
import http
import io
import os
import zipfile
from curses.ascii import isdigit
from datetime import datetime, timedelta, timezone
from typing import Annotated, List, Tuple

import jwt
import qrcode
import reportlab.pdfgen.canvas
import requests
from anyio import SpooledTemporaryFile
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
    StreamingResponse,
)
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import bcrypt
from PIL import Image
from pydantic import BaseModel

from ..config import config
from .jobqueue import ConfirmJobEnum, Job, JobQueue

router = APIRouter()
job_queue = JobQueue(config.results_per_image, config.carrousel_size, config.storage[0])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

"""Hashes a password using bcrypt.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
"""
def hash_password(password: str) -> str:
    return password_context.hash(password)

"""Authenticates a user and generates an access token.

    Args:
        password (str): The password provided by the user.

    Raises:
        HTTPException: If the password is incorrect.

    Returns:
        Token: A JSON object containing the access token and its type.
"""
@router.post("/token")
async def login(password: Annotated[str, Form()]):
    if not bcrypt.checkpw(password.encode('utf-8'), config.password_hash.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = jwt.encode(
        {
            "exp": datetime.now(timezone.utc)  # maybe need to use the correct timezone?
            + timedelta(minutes=config.access_token_expire_time)
        },
        config.secret_key,
        algorithm=config.algorithm,
    )

    return Token(access_token=access_token, token_type="bearer")

"""Validates the provided JWT token.

    Args:
        token (str): The JWT token to validate.

    Raises:
        HTTPException: If the token is invalid.

    Returns:
        bool: True if the token is valid.
"""
def validate_token(token: Annotated[str, Depends(oauth2_scheme)]) -> bool:
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True



qr_generation_progress: float = 0.0

"""Generates QR codes in the background.

    Args:
        n (int): The number of QR codes to generate (must be between 1 and 1000).
        valid (bool): Validates the token for authorization.
        background_tasks (BackgroundTasks): FastAPI's background task manager.

    Returns:
        Response: A message indicating the QR code generation status.
"""
@router.get(
    "/qr",
    responses={200: {"content": {"text/plain": {}}}},
    response_class=Response,
)
def gen_qr_codes(
    n: Annotated[int, Query(gt=0, le=1000)],
    valid: Annotated[bool, Depends(validate_token)],
    background_tasks: BackgroundTasks,  # Inject BackgroundTasks as a parameter
):
    global qr_generation_progress
    qr_generation_progress = 0.0
    # Add the task to the injected background_tasks
    background_tasks.add_task(get_qrs, n)
    return Response(
        content=f"Generating {n} QR codes, this may take a while. Check the progress at /qr/progress",
        media_type="text/plain",
    )

"""Retrieves the progress of QR code generation.

    Args:
        valid (bool): Validates the token for authorization.

    Returns:
        JSONResponse: A JSON object containing the current progress percentage.
"""
@router.get(
    "/qr/progress",
    response_class=JSONResponse,
)
def get_qr_progress(
    valid: Annotated[bool, Depends(validate_token)],
):
    print(f"QR generation progress: {qr_generation_progress}%")
    return JSONResponse(
        content={
            "progress": qr_generation_progress,
        }
    )

"""Handles the download of the generated QR code PDF.

    Args:
        valid (bool): Validates the token for authorization.

    Returns:
        FileResponse: A response containing the QR code PDF file.
"""
@router.get("/qr/download", response_class=FileResponse)
def download_qr_pdf(
    valid: Annotated[bool, Depends(validate_token)],
):
    return FileResponse(
        path="qr.pdf",
        media_type="application/pdf",
        filename="qr.pdf",
    )

"""Generates QR codes and updates the global progress.

    Args:
        n (int): The number of QR codes to generate.

    This function creates QR codes based on a user-specific URL and updates the global
    `qr_generation_progress` variable to reflect the current progress of the generation.
    The generated QR codes are passed to the `gen_qr_pdf` function for PDF creation.
"""
def get_qrs(n):
    global qr_generation_progress
    qr_generation_progress = 0.0
    qrs = []
    for i in range(n):
        url = config.storage[0].create_storage_for_user()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"{url}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qrs.append(img)
        qr.clear()
        qr_generation_progress = i / n * 100
    gen_qr_pdf(qrs)

"""Generates a PDF containing the provided QR code images.

    Args:
        qrs (list): A list of QR code images to include in the PDF.
        size (int, optional): The size of each QR code in the PDF. Defaults to 100.

    This function creates a PDF file named "qr.pdf" that contains the QR codes,
    along with metadata about the storage location and the current date. It also
    manages the layout of the QR codes within the PDF.
"""
def gen_qr_pdf(qrs: list, size: int = 100):
    """
    qrs: list qrcode images
    """
    global qr_generation_progress
    qr_generation_progress = 0.0
    X_BORDER, Y_BORDER, X_SPACING, Y_SPACING = 30, 30, 10, 10
    c = reportlab.pdfgen.canvas.Canvas("qr.pdf")

    def draw_page(c: reportlab.pdfgen.canvas.Canvas):
        """Draws the header and grid layout on the PDF page.

        Args:
            c (Canvas): The ReportLab canvas object to draw on.
        """
        c.drawCentredString(
            300,
            820,
            "Each of the following QR Codes contains a link to an individual storage location",
        )
        # metadata
        c.drawCentredString(50, 820, f"Date:")
        c.drawCentredString(50, 800, f"{datetime.now().date()}")
        c.drawCentredString(550, 820, f"Storage:")
        c.drawCentredString(550, 800, f"{config.storage[0].NAME}")
        c.drawCentredString(
            300, 800, "where the users can view and download their X-Ray results."
        )
        # Draw grid
        for i in [25, 135, 245, 355, 465, 575]:
            c.line(i, 25, i, 795)
        for i in [25, 135, 245, 355, 465, 575, 685, 795]:
            c.line(25, i, 575, i)

    draw_page(c)

    x, y = X_BORDER, Y_BORDER
    for i, img in enumerate(qrs):
        # TODO: this is a hack solution, should draw image from memory and not have to save into file
        os.makedirs("temp", exist_ok=True)
        img.save(f"temp/temp_{i}.png")
        c.drawImage(f"temp/temp_{i}.png", x, y, width=size, height=size)
        x += size + X_SPACING
        if x > 500:
            x = X_BORDER
            y += size + Y_SPACING
            if y >= 800:
                c.showPage()
                draw_page(c)
                x, y = X_BORDER, Y_BORDER
        qr_generation_progress = i / len(qrs) * 100
    c.save()
    qr_generation_progress = 100.0

"""Receives an image of an animal and owner details for processing.

    Args:
        file (UploadFile): The uploaded image file.
        first_name (str): The first name of the owner.
        last_name (str): The last name of the owner.
        animal_name (str): The name of the animal.
        qr_content (str): The QR code content for reference.
        valid (bool): Validates the token for authorization.
        animal_type (str, optional): The type of animal. Defaults to "other".
        broken_bone (bool, optional): Indicates if the animal has a broken bone. Defaults to False.

    Returns:
        dict: A JSON object containing the status of the upload, job ID, and current job count.
"""
@router.post(
    "/upload",
    responses={200: {"content": {"application/json": {}}}},
)
async def create_upload_file(
    file: Annotated[UploadFile, File()],
    first_name: Annotated[str, Form(...)],
    last_name: Annotated[str, Form(...)],
    animal_name: Annotated[str, Form(...)],
    qr_content: Annotated[str, Form(...)],
    valid: Annotated[bool, Depends(validate_token)],
    animal_type: Annotated[str, Form()] = "other",  # TODO: add validator
    broken_bone: Annotated[bool, Form()] = False,
):
    """Receive image of a teddy and user id so that we know where to save later.
    the image itself also gets an id so it can be referenced later when receiving results
    from AI."""
    f = SpooledTemporaryFile()
    await f.write(await file.read())
    job = Job(
        file=f,
        owner_ref=qr_content,
        first_name=first_name,
        last_name=last_name,
        animal_name=animal_name,
        animal_type=animal_type,
        broken_bone=broken_bone,
        number_of_results=config.results_per_image,
    )
    job_queue.add_job(job)
    return {"status": "success", "job_id": job.id, "current_jobs": len(job_queue.queue)}

"""Retrieves a job from the queue and returns the associated image.

    Args:
        valid (bool): Validates the token for authorization.

    Returns:
        Response: An image response with job details or a 204 status if no jobs are available.
"""
@router.get(
    "/job",
    responses={
        200: {"content": {"image/png": {}}},
        204: {"description": "No Jobs in queue"},
    },
    response_class=Response,
)
async def get_job(
    valid: Annotated[bool, Depends(validate_token)],
):
    """
    Get job from the queue. Returns an image with an id.
    """
    job = job_queue.get_job()
    if job is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    await job.file.seek(0)
    response = Response(
        content=await job.file.read(), media_type="image/png", status_code=200
    )
    response.headers["Content-Type"] = "image/png"
    response.headers["img_id"] = str(job.id)
    response.headers["first_name"] = job.first_name
    response.headers["last_name"] = job.last_name
    response.headers["animal_name"] = job.animal_name
    response.headers["animal_type"] = job.animal_type
    return response

"""Submits the result of a job for processing.

    Args:
        image_id (int): The ID of the job to conclude.
        result (UploadFile): The result image file to be submitted.
        valid (bool): Validates the token for authorization.

    Returns:
        dict: A JSON object indicating the success of the submission.
"""
@router.post("/job", responses={200: {"content": {"application/json": {}}}})
async def conclude_job(
    image_id: Annotated[int, Form()],
    result: Annotated[UploadFile, File()],
    valid: Annotated[bool, Depends(validate_token)],
):
    await job_queue.submit_job(image_id, await result.read())
    return {"status": "success"}

"""Confirms a job based on user input.

    Args:
        image_id (int): The ID of the job to confirm.
        choice (int): The user's choice regarding the job.
        confirm (ConfirmJobEnum): The confirmation status.
        valid (bool): Validates the token for authorization.

    Returns:
        JSONResponse: A JSON object indicating the success of the confirmation.
"""
@router.get("/confirm")
async def confirm_job(
    image_id: Annotated[int, Query()],
    choice: Annotated[int, Query()],
    confirm: Annotated[ConfirmJobEnum, Query()],
    valid: Annotated[bool, Depends(validate_token)],
):
    await job_queue.confirm_job(image_id, confirm, choice)
    return JSONResponse(content={"status": "success"})

"""Retrieves the results of jobs awaiting approval.

    Args:
        valid (bool): Validates the token for authorization.
        request (Request): The FastAPI request object to construct URLs.

    Returns:
        JSONResponse: A JSON object containing metadata, result URLs, and original image URLs for each job.
"""
@router.get("/results")
async def get_results(
    valid: Annotated[bool, Depends(validate_token)], request: Request
) -> JSONResponse:
    # Compare job_queue.awaiting_approval with current_results
    # return dict with key = job_id and value = list of urls for the results
    results: dict[int, list[str]] = {}
    originals: dict[int, str] = {}
    metadata: dict[int, dict] = {}
    for k, v in job_queue.awaiting_approval.items():
        results[k] = [
                str(request.url_for("get_result_image", job_id=k, option=str(option)))
            for option in range(len(v[1]))
        ]
        results[k] = results[k] + ["nonsense"] * (config.results_per_image - len(v[1]))
        originals[k] = (
                str(request.url_for("get_result_image", job_id=k, option="original"))
        )
        job = v[0]
        metadata[k] = {
            "first_name": job.first_name,
            "last_name": job.last_name,
            "animal_name": job.animal_name,
        }
    response = {
        "metadata": metadata,
        "results": results,
        "originals": originals,
        "results_per_image": config.results_per_image,
    }
    return JSONResponse(content=response)

"""Retrieves a specific result image for a given job.

    Args:
        job_id (int): The ID of the job whose result is being requested.
        option (str): The option index of the result image.

    Returns:
        StreamingResponse: A streaming response containing the requested image.
"""
@router.get("/results/{job_id}/{option}", response_class=StreamingResponse)
async def get_result_image(
    job_id: Annotated[int, Path()], option: Annotated[str, Path()]
):
    if option.isdigit():
        options = job_queue.awaiting_approval[job_id][1]
        file = options[int(option)]
        await file.seek(0)
        response = StreamingResponse(content=file, media_type="image/png")
    else:
        job = job_queue.awaiting_approval[job_id][0]
        file = job.file
        await file.seek(0)

        response = StreamingResponse(content=file, media_type="image/png")

    # these headers are for fixing cache issue
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

"""Retrieves the list of available animal types.

    Returns:
        JSONResponse: A JSON object containing the available animal types.
"""
@router.get("/animal_types", response_class=JSONResponse)
def get_animal_types():
    return JSONResponse({"types": config.animal_types})


"""Retrieves a list of URLs for carousel images.

    Args:
        request (Request): The FastAPI request object to construct URLs.

    Returns:
        JSONResponse: A JSON object containing URLs for carousel images.
"""
@router.get("/carousel", response_class=JSONResponse)
async def get_carousel_list(request: Request):
    # Returns a list of URLs to fetch carousel images.
    carousel_items = job_queue.get_carousel()
    return JSONResponse(
        content=[
            str(request.url_for("get_carousel_image", index=i))
            for i in range(len(carousel_items))
        ]
    )


"""Retrieves a zip file containing X-ray and original images for a specific carousel index.

    Args:
        index (int): The index of the carousel item to retrieve.

    Returns:
        StreamingResponse: A streaming response containing a zip file with the images, or a 404 status if the index is invalid.
"""
@router.get("/carousel/{index}")
async def get_carousel_image(index: int):
    carousel = job_queue.get_carousel()
    if index < 0 or index >= len(carousel):
        return Response(status_code=404)

    xray_file, original_file = carousel[index]
    await xray_file.seek(0)
    await original_file.seek(0)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("xray.png", await xray_file.read())
        zip_file.writestr("original.png", await original_file.read())
    zip_buffer.seek(0)

    headers = {"Content-Disposition": f"attachment; filename=carousel_{index}.zip"}

    return StreamingResponse(zip_buffer, media_type="application/zip", headers=headers)
