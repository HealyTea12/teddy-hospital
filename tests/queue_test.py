from unittest.mock import Mock

import pytest
from anyio import SpooledTemporaryFile
from PIL import Image
from PIL.Image import Transpose

from backend.routes.jobqueue import Job, JobQueue, Result
from tests.conftest import MockStorage

@pytest.fixture
def storage_mock():
    return Mock()

# mock storage for testing
# results_per_image = 2, carrousel_size=3
@pytest.fixture
def jobqueue(storage_mock):
    return JobQueue(results_per_image=2, carrousel_size=3, storage=storage_mock)

# mock function to create a job for a picture with the name Teddy (owner Max Mustermann)
def create_mock_job():
    file_mock = Mock(spec=SpooledTemporaryFile)
    file_mock.wrapped = "original_data"
    return Job(file=file_mock, owner_ref="upload_link", first_name="Max", last_name="Mustermann", animal_name="Teddy")


# check if init is correct
# everything should be empty
def test_jobqueue_initialization(storage_mock):
    queue = JobQueue(results_per_image=2, carrousel_size=3, storage=storage_mock)
    assert queue.queue == []
    assert queue.in_progress == {}
    assert queue.awaiting_approval == {}
    assert queue.carrousel == []

# test adding a job to queue and removing it, other words insert then pop
# expected: queue empty, inprogress has job
def test_add_and_get_job(jobqueue):
    job = create_mock_job()
    jobqueue.add_job(job)
    job_from_queue = jobqueue.get_job()

    assert job_from_queue == job
    assert job.id in jobqueue.in_progress
    assert jobqueue.queue == []


# test submitting results to queue
# expected: since result_per_image is set to 2, the first submission should not move the job to awaiting_approval
# only when the second result is submitted should the job move to awaiting_approval
def test_submit_job_to_approval(jobqueue):
    job = create_mock_job()
    jobqueue.add_job(job)
    job = jobqueue.get_job()

    result1 = Mock(spec=SpooledTemporaryFile)
    result2 = Mock(spec=SpooledTemporaryFile)

    jobqueue.submit_job(job.id, result1)
    assert job.id not in jobqueue.awaiting_approval

    jobqueue.submit_job(job.id, result2)
    assert job.id in jobqueue.awaiting_approval
    assert len(jobqueue.awaiting_approval[job.id][1]) == 2


# test confirming a job
# expected: after approval the awaiting_approval queue should be empty, the chosen picture should be saved in storage
@pytest.mark.asyncio
async def test_confirm_job_approve(jobqueue, storage_mock):
    job = create_mock_job()
    jobqueue.add_job(job)
    job = jobqueue.get_job()

    result = Mock(spec=SpooledTemporaryFile)
    result.wrapped = "xray_data"
    jobqueue.submit_job(job.id, result)
    jobqueue.submit_job(job.id, result)

    await jobqueue.confirm_job(job.id, confirm=True, choice=0)

    # check if the file is saved
    storage_mock.upload_file.assert_any_call(job.owner_ref, "normal", "original_data")
    storage_mock.upload_file.assert_any_call(job.owner_ref, "xray", "xray_data")
    assert len(jobqueue.carrousel) == 1
    assert job.id not in jobqueue.awaiting_approval

# test when no pictures were approved
# expected: job should now be in jobqueue
@pytest.mark.asyncio
async def test_confirm_job_reject(jobqueue):
    job = create_mock_job()
    jobqueue.add_job(job)
    job = jobqueue.get_job()

    result1 = Mock(spec=SpooledTemporaryFile)
    result2 = Mock(spec=SpooledTemporaryFile)
    jobqueue.submit_job(job.id, result1)
    jobqueue.submit_job(job.id, result2)

    await jobqueue.confirm_job(job.id, confirm=False, choice=0)

    result1.aclose.assert_called_once()
    result2.aclose.assert_called_once()
    assert job in jobqueue.queue
    assert job.id not in jobqueue.awaiting_approval

# check for invalid id usage
def test_submit_invalid_id(jobqueue):
    with pytest.raises(ValueError):
        jobqueue.submit_job(999, Mock())


@pytest.mark.asyncio
async def test_confirm_invalid_id(jobqueue):
    with pytest.raises(ValueError):
        await jobqueue.confirm_job(999, confirm=True, choice=0)

# test out of bounds
@pytest.mark.asyncio
async def test_confirm_invalid_choice_index(jobqueue):
    job = create_mock_job()
    jobqueue.add_job(job)
    job = jobqueue.get_job()

    result = Mock(spec=SpooledTemporaryFile)
    jobqueue.submit_job(job.id, result)
    jobqueue.submit_job(job.id, result)

    with pytest.raises(IndexError):
        await jobqueue.confirm_job(job.id, confirm=True, choice=5)
