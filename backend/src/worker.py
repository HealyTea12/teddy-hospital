import datetime
from PIL import Image, ImageOps
from io import BytesIO
from celery import Celery
from pathlib import Path

celery_app = Celery(
    "tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1"
)


def flip_image_colors(image_data: bytes) -> bytes:
    image = Image.open(BytesIO(image_data)).convert("RGB")
    inverted_image = ImageOps.invert(image)
    output = BytesIO()
    inverted_image.save(output, format="PNG")
    return output.getvalue()


OUTPUT_DIR = Path("images/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@celery_app.task
def process_image_task(image_bytes: bytes) -> str:
    flipped_image_bytes = flip_image_colors(image_bytes)

    # Create a timestamp-based filename
    filename = (
        f"flipped_{datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S%f')}.png"
    )
    file_path = OUTPUT_DIR / filename

    # Save the image
    with open(file_path, "wb") as f:
        f.write(flipped_image_bytes)

    return str(file_path)  # Return path as result
