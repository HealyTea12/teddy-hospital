from unittest import mock

import pytest
from anyio import SpooledTemporaryFile
from PIL import Image
from PIL.Image import Transpose

from backend.routes.jobqueue import ConfirmJobEnum, Job, JobQueue, Result
from tests.conftest import MockStorage


async def flip(f: SpooledTemporaryFile) -> list[SpooledTemporaryFile[bytes]]:
    await f.seek(0)
    f1 = SpooledTemporaryFile()
    f2 = SpooledTemporaryFile()
    f3 = SpooledTemporaryFile()
    img = Image.open(f.wrapped)
    img.transpose(Transpose.FLIP_TOP_BOTTOM).save(f1.wrapped, "png")
    img.transpose(Transpose.FLIP_LEFT_RIGHT).save(f2.wrapped, "png")
    img.transpose(Transpose.ROTATE_90).save(f3.wrapped, "png")
    return [f1, f2, f3]


@pytest.mark.anyio
class TestJobQueue:
    async def test_job_queue(self, mock_storage):
        job_queue = JobQueue(
            results_per_image=3, carrousel_size=3, storage=mock_storage
        )
        sf1 = SpooledTemporaryFile()
        sf2 = SpooledTemporaryFile()
        sf3 = SpooledTemporaryFile()
        f1 = open("tests/img/eichhornchen.jpeg", "rb")
        f2 = open("tests/img/teddy.jpg", "rb")
        f3 = open("tests/img/own.jpg", "rb")
        await sf1.write(f1.read())
        await sf2.write(f2.read())
        await sf3.write(f3.read())
        job = Job(
            file=sf1,
            owner_ref=1,
            first_name="Test",
            last_name="User",
            animal_name="Eichhornchen",
            animal_type="squirrel",
            broken_bone=False,
        )
        job2 = Job(
            file=sf2,
            owner_ref=1,
            first_name="Test",
            last_name="User",
            animal_name="Teddy",
            animal_type="bear",
            broken_bone=False,
        )
        job3 = Job(
            file=sf3,
            owner_ref=1,
            first_name="Test",
            last_name="User",
            animal_name="Own",
            animal_type="other",
            broken_bone=False,
        )
        job_queue.add_job(job)
        job_queue.add_job(job2)
        job_queue.add_job(job3)
        assert len(job_queue.queue) == 3
        assert len(job_queue.in_progress) == 0
        assert len(job_queue.awaiting_approval) == 0
        assert job_queue.get_job() == job
        assert job_queue.get_job() == job2
        assert job_queue.get_job() == job3
        assert job_queue.get_job() is None

    async def test_submit_job(self, mock_storage: MockStorage):
        job_queue = JobQueue(
            results_per_image=3, carrousel_size=3, storage=mock_storage
        )
        mock_storage.create_storage_for_user()
        mock_storage.create_storage_for_user()
        sf1 = SpooledTemporaryFile()
        sf2 = SpooledTemporaryFile()
        sf3 = SpooledTemporaryFile()
        f1 = open("tests/img/eichhornchen.jpeg", "rb")
        f2 = open("tests/img/teddy.jpg", "rb")
        f3 = open("tests/img/own.jpg", "rb")
        await sf1.write(f1.read())
        await sf2.write(f2.read())
        await sf3.write(f3.read())
        job_queue.add_job(
            Job(
                file=sf1,
                owner_ref=1,
                first_name="Test",
                last_name="User",
                animal_name="Eichhornchen",
                animal_type="squirrel",
                broken_bone=False,
            )
        )
        job_queue.add_job(
            Job(
                file=sf2,
                owner_ref=1,
                first_name="Test",
                last_name="User",
                animal_name="Teddy",
                animal_type="bear",
                broken_bone=False,
            )
        )
        job_queue.add_job(
            Job(
                file=sf3,
                owner_ref=1,
                first_name="Test",
                last_name="User",
                animal_name="Own",
                animal_type="other",
                broken_bone=False,
            )
        )
        job = job_queue.get_job()
        assert job is not None
        assert len(job_queue.queue) == 2
        assert len(job_queue.in_progress) == 1
        mocked_result = await flip(job.file)
        job_queue.submit_job(job.id, mocked_result[0])
        job_queue.submit_job(job.id, mocked_result[1])
        assert len(job_queue.queue) == 2
        assert len(job_queue.in_progress) == 1
        assert len(job_queue.awaiting_approval) == 0
        job_queue.submit_job(job.id, mocked_result[2])
        assert len(job_queue.queue) == 2
        assert len(job_queue.in_progress) == 0
        assert len(job_queue.awaiting_approval) == 1
        await job_queue.confirm_job(job.id, ConfirmJobEnum.confirm, 0)
        assert len(job_queue.awaiting_approval) == 0
        await mocked_result[0].seek(0)
        assert mock_storage.storage[1]["xray"] == await mocked_result[0].read()
