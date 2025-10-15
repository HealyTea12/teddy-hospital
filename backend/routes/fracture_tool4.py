import tempfile
from io import BytesIO
from typing import Annotated

import cv2
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from PIL import Image

router = APIRouter()


# ------------------- Helper functions


def add_gaussian_noise(image: np.ndarray, mean: float = 0, std: float = 10):
    noise = np.random.normal(mean, std, image.shape).astype(np.int16)
    noisy = np.clip(image.astype(np.int16) + noise, 0, 255)
    return noisy.astype(np.uint8)


def sample_color_gradient(img: np.ndarray, mask: np.ndarray, x: int, y: int):
    # Grey Threshold for samples (only sampling, if lower than Threshold)
    gray_thresh = 120
    x = x % img.shape[1]
    y = y % img.shape[0]
    h, w = mask.shape
    center_x = x + w // 2
    center_y = y + h // 2
    max_radius = max(h, w) // 2
    alpha_mask = mask / 255.0

    sample1 = sample2 = None
    dir_vector = np.array([0, 0])

    # Searching first Sample:
    for r in range(1, max_radius):
        for angle in np.linspace(0, 2 * np.pi, 64):
            dx = int(round(r * np.cos(angle)))
            dy = int(round(r * np.sin(angle)))
            sx = center_x + dx
            sy = center_y + dy

            if 0 <= sx < img.shape[1] and 0 <= sy < img.shape[0]:
                if np.mean(img[sy, sx]) < gray_thresh:
                    sample1 = (sx, sy)
                    dir_vector = np.array([dx, dy])
                    break
        if sample1 is not None:
            break

    if sample1 is None:
        return img[50, 50].astype(np.float32), img[1, 1].astype(np.float32), (1, 0)

    # Search Second Sample
    for r in range(1, max_radius):
        dx, dy = -dir_vector * r
        sx = center_x + int(round(dx))
        sy = center_y + int(round(dy))

        mask_y = sy - y
        mask_x = sx - x
        if (
            0 <= sx < img.shape[1]
            and 0 <= sy < img.shape[0]
            and 0 <= mask_x < alpha_mask.shape[1]
            and 0 <= mask_y < alpha_mask.shape[0]
        ):
            if alpha_mask[mask_y, mask_x] > 0 and np.mean(img[sy, sx]) < gray_thresh:
                sample2 = (sx, sy)
                break

    if sample2 is None:
        return (
            img[1, 1].astype(np.float32),
            img[sample1[1], sample1[0]].astype(np.float32),
            dir_vector,
        )

    color1 = img[sample1[1], sample1[0]].astype(np.float32)
    color2 = img[sample2[1], sample2[0]].astype(np.float32)
    gradient_direction = np.array(sample2) - np.array(sample1)

    return color1, color2, gradient_direction


def apply_gradient_to_mask(
    img: np.ndarray,
    x: int,
    y: int,
    overlay: np.ndarray,
    gradient_dir: np.ndarray,
    color1: np.ndarray,
    color2: np.ndarray,
    noise_std: int,
):
    UPPER_TRESH_MASK = np.array(255)
    LOWER_TRESH_MASK = np.array(90)
    x = x % img.shape[1]  # Corrections in case of wrong coordinates: Image width
    y = y % img.shape[0]  # Image height
    print(x)
    print(y)
    x = int(x)
    y = int(y)
    h, w = overlay.shape[:2]

    # Fallback for zero_gradient
    if np.allclose(gradient_dir, 0):
        gradient_dir = np.array([1, 0], dtype=float)

    start_x = max(0, x)
    start_y = max(0, y)
    end_x = min(x + w, img.shape[1])
    end_y = min(y + h, img.shape[0])

    roi = img[start_y:end_y, start_x:end_x]
    overlay = overlay[(start_y - y) : (end_y - y), (start_x - x) : (end_x - x)]

    if overlay.shape[0] == 0 or overlay.shape[1] == 0:
        return img  # overlay not valid

    alpha = overlay[:, :, 3] / 255.0
    mask = np.repeat(alpha[..., np.newaxis], 3, axis=2)

    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    bone_mask = cv2.inRange(gray_roi, LOWER_TRESH_MASK, UPPER_TRESH_MASK) / 255.0

    # make Mask bigger
    kernel = np.ones((3, 3), np.uint8)
    bone_mask_expanded = (
        cv2.dilate((bone_mask * 255).astype(np.uint8), kernel, iterations=1) / 255.0
    )
    bone_mask_3ch = np.repeat(bone_mask_expanded[..., np.newaxis], 3, axis=2)

    combined_mask = mask * bone_mask_3ch

    # calculate Gradient direction
    grad_norm = gradient_dir / (np.linalg.norm(gradient_dir) + 1e-6)
    Y, X = np.meshgrid(
        np.arange(overlay.shape[0]), np.arange(overlay.shape[1]), indexing="ij"
    )
    rel_coords = np.stack(
        (X - overlay.shape[1] // 2, Y - overlay.shape[0] // 2), axis=-1
    )
    projections = rel_coords @ grad_norm

    # Fallback for empty alpha_mask
    mask_nonzero = alpha > 0
    if np.any(mask_nonzero):
        min_proj = np.min(projections[mask_nonzero])
        max_proj = np.max(projections[mask_nonzero])
    else:
        min_proj, max_proj = 0.0, 1.0

    norm_proj = (projections - min_proj) / (max_proj - min_proj + 1e-6)
    norm_proj = np.clip(norm_proj, 0, 1)

    # Add gradient
    gradient = (1 - norm_proj[..., None]) * color1 + norm_proj[..., None] * color2
    gradient_noisy = add_gaussian_noise(gradient.astype(np.uint8), std=noise_std)

    blended = (1 - combined_mask) * roi + combined_mask * gradient_noisy

    img[start_y:end_y, start_x:end_x] = blended.astype(np.uint8)
    return img


def apply_fracture(
    img: np.ndarray, overlay: np.ndarray, x: int, y: int, scale: float, noise_std: int
):
    overlay_resized = cv2.resize(overlay, (0, 0), fx=scale, fy=scale)
    h, w = overlay_resized.shape[:2]
    if y + h > img.shape[0] or x + w > img.shape[1]:
        return img

    alpha = overlay_resized[:, :, 3]
    color1, color2, grad_dir = sample_color_gradient(img, alpha, x, y)
    return apply_gradient_to_mask(
        img, x, y, overlay_resized, grad_dir, color1, color2, noise_std
    )


@router.post("/apply_fracture")
def fracture(
    x: Annotated[int, Form()],
    y: Annotated[int, Form()],
    scale: Annotated[float, Form()],
    noise: Annotated[int, Form()],
    image_file: Annotated[UploadFile, File()],
    overlay_file: Annotated[UploadFile, File()],
):

    image_np = cv2.imdecode(
        np.frombuffer(image_file.file.read(), np.uint8), cv2.IMREAD_COLOR
    )
    overlay_np = cv2.imdecode(
        np.frombuffer(overlay_file.file.read(), np.uint8), cv2.IMREAD_UNCHANGED
    )
    if image_np is None or overlay_np is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image or overlay file",
        )
    result_img = apply_fracture(image_np.copy(), overlay_np, x, y, scale, noise)

    _, encoded_img = cv2.imencode(".png", result_img)
    with tempfile.NamedTemporaryFile(
        delete=False
    ) as temp_file:  # temporaryily don't delete file, need to delete manually later
        temp_file.write(encoded_img.tobytes())
        temp_file.seek(0)
        return FileResponse(
            temp_file.name,
            media_type="image/png",
            filename="fractured_image.png",
        )
