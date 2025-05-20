from tkinter import Image
from typing import NamedTuple, Tuple

from anyio import SpooledTemporaryFile

from ..config import config

ImageInMemoryStorageT = SpooledTemporaryFile[bytes]


# a file plus an owner id or an upload link, haven't decided yet
class Job:
    def __init__(self, file: ImageInMemoryStorageT, owner_ref: int | str):
        self.file = file
        self.owner_ref = owner_ref  # either id or upload link


Result = list[SpooledTemporaryFile]


class JobQueue:
    def __init__(self):
        # Queue holding spooled temporary files because the memory might get full and
        # it supports async operations
        self.queue: list[Job] = []
        # dictionary holding the images being processed
        self.in_progress: dict[int, Job] = {}
        # first is the original and the following are results from the AI
        self.awaiting_approval: dict[int, Tuple[Job, Result]] = {}
        self.next_id: int = 0

    def get_job(self) -> None | Tuple[ImageInMemoryStorageT, int]:
        if len(self.queue) == 0:
            return None
        job = self.queue.pop()
        self.in_progress[self.next_id] = job
        self.next_id += 1
        return job.file, self.next_id - 1

    def add_job(self, item: Job) -> None:
        self.queue.insert(0, item)

    def submit_job(self, id: int, result: Result) -> None:
        if id not in self.in_progress:
            raise ValueError("Invalid id")
        job = self.in_progress.pop(id)
        self.awaiting_approval[id] = (job, result)

    async def confirm_job(self, id: int, confirm: bool, choice: int) -> None:
        if id not in self.awaiting_approval:
            raise ValueError("Invalid id")
        job, results = self.awaiting_approval.pop(id)
        if confirm:
            config.storage[0].upload_file(
                job.owner_ref,
                "normal",
                job.file,
            )
            config.storage[0].upload_file(
                job.owner_ref,
                "xray",
                results.files[choice],
            )
        else:
            for file in results.files:
                await file.aclose()
            self.add_job(job)
