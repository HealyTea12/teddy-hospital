from enum import Enum, StrEnum, auto
from typing import Tuple

from anyio import SpooledTemporaryFile
from fastapi import UploadFile

from ..storage import Storage

ImageInMemoryStorageT = SpooledTemporaryFile[bytes]

"""Represents a job that includes an image file and associated metadata.

    Attributes:
        c_id (int): A class variable to keep track of the job IDs.
        file (ImageInMemoryStorageT): The image file associated with the job.
        owner_ref (int | str): A reference for the owner, either an ID or an upload link.
        first_name (str): The first name of the owner.
        last_name (str): The last name of the owner.
        animal_name (str): The name of the animal associated with the job.
        animal_type (str): The type of animal. Defaults to "other".
        broken_bone (bool): Indicates if the animal has a broken bone. Defaults to False.
        id (int): The unique ID of the job.
        number_of_results (int): The number of results expected for this job.
"""


# a file plus an owner id or an upload link, haven't decided yet
class Job:
    c_id = 0

    def __init__(
        self,
        file: ImageInMemoryStorageT,
        owner_ref: int | str,
        first_name: str,
        last_name: str,
        animal_name: str,
        animal_type: str = "other",
        broken_bone: bool = False,
        number_of_results: int = 1,
    ):
        self.file = file
        self.owner_ref = owner_ref  # either id or upload link
        self.first_name = first_name
        self.last_name = last_name
        self.animal_name = animal_name
        self.animal_type = animal_type
        self.broken_bone = broken_bone
        self.id = Job.c_id
        self.number_of_results = number_of_results
        Job.c_id += 1


Result = list[SpooledTemporaryFile[bytes]]

"""Enumeration for job confirmation statuses."""


class ConfirmJobEnum(StrEnum):
    confirm = auto()
    retry = auto()
    cancel = auto()


"""Manages a queue of jobs and their associated results.

    Attributes:
        queue (list[Job]): A list of jobs currently in the queue.
        awaiting_approval (dict[int, Tuple[Job, Result]]): A dictionary mapping job IDs to jobs and their results.
        carrousel (list[Tuple[SpooledTemporaryFile, SpooledTemporaryFile]]): A list of images for the carousel.
        carrousel_size (int): The maximum number of images allowed in the carousel.
        results_per_image (int): The number of results expected for each image.
        storage (Storage): The storage system used to upload files.
"""


class JobQueue:
    def __init__(self, results_per_image: int, carrousel_size: int, storage: Storage):
        # Queue holding spooled temporary files because the memory might get full and
        # it supports async operations
        self.queue: list[Job] = []
        # first is the original and the following are results from the AI
        self.awaiting_approval: dict[int, Tuple[Job, Result]] = {}
        # queue manages the carrousel
        self.carrousel: list[Tuple[SpooledTemporaryFile, SpooledTemporaryFile]] = []
        self.carrousel_size = carrousel_size
        self.results_per_image = results_per_image
        self.storage = storage

    """Retrieves the next job from the queue.

        Returns:
            Job | None: The next job in the queue or None if the queue is empty.
    """

    def get_job(self) -> None | Job:
        if len(self.queue) == 0:
            return None
        job = self.queue[-1]
        job.number_of_results -= 1
        if job.number_of_results <= 0:
            self.queue.pop()
        return job

    """Adds a new job to the queue.

        Args:
            job (Job): The job to be added to the queue.
    """

    def add_job(self, job: Job) -> None:
        self.queue.insert(0, job)
        self.awaiting_approval[job.id] = job, []

    """Submits the result for a specific job.

        Args:
            id (int): The ID of the job to which the result belongs.
            result (bytes): The result data to be submitted.

        Raises:
            ValueError: If the job ID is invalid.
    """

    async def submit_job(self, id: int, result: bytes) -> None:
        stf = SpooledTemporaryFile[bytes]()
        await stf.write(result)
        if id not in self.awaiting_approval:
            raise ValueError("Invalid id")
        entry = self.awaiting_approval[id]
        entry[1].append(stf)

    """Confirms the status of a job based on user input.

        This method handles the confirmation of a job, including uploading the original
        and result images to storage, retrying the job, or canceling it.

        Args:
            id (int): The ID of the job to confirm.
            confirm (ConfirmJobEnum): The confirmation status (confirm, retry, or cancel).
            choice (int): The index of the result to upload if confirmed.

        Raises:
            ValueError: If the job ID is invalid.

        This method performs the following actions based on the confirmation status:
            - If confirmed, it uploads the original image and the selected result image to storage,
              and adds the result to the carousel.
            - If retrying, it closes the result files and re-adds the job to the queue.
            - If canceled, it closes all associated files and removes the job from the queue.
    """

    async def confirm_job(
        self, id: int, confirm: ConfirmJobEnum, choice: int, image: UploadFile | None
    ) -> None:
        if id not in self.awaiting_approval:
            raise ValueError("Invalid id")
        job, results = self.awaiting_approval.pop(id)
        if image is not None:
            results[choice] = SpooledTemporaryFile[bytes]()
            await image.seek(0)
            await results[choice].write(await image.read())
            await results[choice].seek(0)

        # Remove the job from the queue if it exist
        if job in self.queue:
            self.queue.remove(job)
        if confirm == ConfirmJobEnum.confirm:
            await job.file.seek(0)

            # Upload the original image to storage
            self.storage.upload_file(
                job.owner_ref,
                "normal",
                job.file.wrapped,
                f"{job.id}_original.png",
            )
            await results[choice].seek(0)

            # Upload the selected result image to storage
            self.storage.upload_file(
                job.owner_ref,
                "xray",
                results[choice].wrapped,
                f"{job.id}_result.png",
            )
            # Add the result to the carousel
            self.carrousel.insert(0, (results[choice], job.file))
            # Maintain the carousel size limit
            if len(self.carrousel) > self.carrousel_size:
                self.carrousel.pop()
        elif confirm == ConfirmJobEnum.retry:
            # Close all result files and re-add the job to the queue
            for file in results:
                await file.aclose()
            job.number_of_results = self.results_per_image
            self.add_job(job)
        else:  # confirm == ConfirmJobEnum.cancel
            # Close all result files and the job file
            for file in results:
                await file.aclose()
            await job.file.aclose()

    """Retrieves the current list of images in the carousel.

        Returns:
            list[Tuple[SpooledTemporaryFile, SpooledTemporaryFile]]: A list of tuples containing
            the X-ray and original images in the carousel.
    """

    def get_carousel(self) -> list[Tuple[SpooledTemporaryFile, SpooledTemporaryFile]]:
        return self.carrousel
