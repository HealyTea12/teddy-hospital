from io import BytesIO

import requests
from anyio import sleep
from PIL import Image
from PIL.Image import Transpose


def flip(f: bytes) -> list[bytes]:
    img = Image.open(BytesIO(f))
    f1 = BytesIO()
    f2 = BytesIO()
    f3 = BytesIO()
    img.transpose(Transpose.FLIP_TOP_BOTTOM).save(f1, "png")
    img.transpose(Transpose.FLIP_LEFT_RIGHT).save(f2, "png")
    img.transpose(Transpose.ROTATE_90).save(f3, "png")
    return [f1.getvalue(), f2.getvalue(), f3.getvalue()]


async def run():
    while True:
        print("requesting job")
        r = requests.get("http://localhost:8000/job")
        if r.headers["Content-Type"] != "image/png":
            print("no job available")
            await sleep(5)
            continue
        file = r.content
        img_id = r.headers["img_id"]
        results = flip(file)
        print(f"received job {img_id}")
        print("submitting result1")
        r1 = requests.post(
            "http://localhost:8000/job",
            headers={"image-id": img_id},
            files={"result": ("test_result.png", results[0], "image/png")},
        )
        print(r1.status_code, r1.text)
        await sleep(5)
        print("submitting result2")
        r2 = requests.post(
            "http://localhost:8000/job",
            headers={"image-id": img_id},
            files={"result": ("test_result.png", results[1], "image/png")},
        )
        await sleep(5)
        print("submitting result3")
        r3 = requests.post(
            "http://localhost:8000/job",
            headers={"image-id": img_id},
            files={"result": ("test_result.png", results[2], "image/png")},
        )
        await sleep(2)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
