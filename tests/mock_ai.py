import random
from io import BytesIO

import requests
from anyio import sleep
from PIL import Image
from PIL.Image import Transpose

BACKEND_URL = "https://ssc-teddy.iwr.uni-heidelberg.de/api"
PASSWORD = "Password"


def flip(f: bytes) -> bytes:
    img = Image.open(BytesIO(f))
    operations = [
        Transpose.FLIP_TOP_BOTTOM,
        Transpose.FLIP_LEFT_RIGHT,
        Transpose.ROTATE_90,
    ]
    op = random.choice(operations)
    f1 = BytesIO()
    img.transpose(op).save(f1, "png")
    return f1.getvalue()


async def run():
    token = requests.post(
        f"{BACKEND_URL}/token", data={"password": f"{PASSWORD}"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    while True:
        print("requesting job")
        r = requests.get(f"{BACKEND_URL}/job", headers=headers)
        if r.status_code == 204:
            print("no job available")
            await sleep(5)
            continue
        if r.status_code == 401:
            print("unauthorized, retrying")
            token = requests.post(
                f"{BACKEND_URL}/token", data={"password": f"{PASSWORD}"}
            ).json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
        if r.status_code != 200:
            print(f"error: {r.status_code} {r.text}")
            await sleep(5)
            continue
        file = r.content
        img_id = r.headers["img_id"]
        result = flip(file)
        print(f"received job {img_id}")
        print("submitting result1")
        r1 = requests.post(
            f"{BACKEND_URL}/job",
            headers=headers,
            files={"result": ("test_result.png", result, "image/png")},
            data={"image_id": img_id},
        )
        await sleep(5)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
