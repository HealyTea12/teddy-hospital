from tkinter import Image
from typing import NamedTuple, Tuple

from anyio import SpooledTemporaryFile

from ..storage import Storage

ImageInMemoryStorageT = SpooledTemporaryFile[bytes]


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
    ):
        self.file = file
        self.owner_ref = owner_ref  # either id or upload link
        self.first_name = first_name
        self.last_name = last_name
        self.animal_name = animal_name
        self.animal_type = animal_type
        self.broken_bone = broken_bone
        self.id = Job.c_id
        Job.c_id += 1


Result = list[SpooledTemporaryFile[bytes]]


class JobQueue:
    def __init__(self, results_per_image: int, carrousel_size: int, storage: Storage):
        # Queue holding spooled temporary files because the memory might get full and
        # it supports async operations
        self.queue: list[Job] = []
        # dictionary holding the images being processed
        self.in_progress: dict[int, Tuple[Job, Result]] = {}
        # first is the original and the following are results from the AI
        self.awaiting_approval: dict[int, Tuple[Job, Result]] = {}
        # queue manages the carrousel
        self.carrousel: list[SpooledTemporaryFile[bytes]] = []
        self.carrousel_size = carrousel_size
        self.results_per_image = results_per_image
        self.storage = storage

    def get_job(self) -> None | Job:
        if len(self.queue) == 0:
            return None
        job = self.queue.pop()
        self.in_progress[job.id] = job, []
        return job

    def add_job(self, item: Job) -> None:
        self.queue.insert(0, item)

    def submit_job(self, id: int, result: SpooledTemporaryFile) -> None:
        if id not in self.in_progress:
            raise ValueError("Invalid id")
        entry = self.in_progress[id]
        entry[1].append(result)
        if len(entry[1]) == self.results_per_image:
            entry = self.in_progress.pop(id)
            self.awaiting_approval[id] = entry

    async def confirm_job(self, id: int, confirm: bool, choice: int) -> None:
        if id not in self.awaiting_approval:
            raise ValueError("Invalid id")
        job, results = self.awaiting_approval.pop(id)
        if confirm:
            self.storage.upload_file(
                job.owner_ref,
                "normal",
                job.file.wrapped,
            )
            self.storage.upload_file(
                job.owner_ref,
                "xray",
                results[choice].wrapped,
            )
            self.carrousel.insert(0, results[choice])
            if len(self.carrousel) > self.carrousel_size:
                self.carrousel.pop()
        else:
            for file in results:
                await file.aclose()
            self.add_job(job)
