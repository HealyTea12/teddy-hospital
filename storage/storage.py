from abc import ABC, abstractmethod
from typing import override
from urllib.parse import quote

import requests

from seafile import SeafileAPI


class Storage(ABC):
    """
    Base class for storage systems.
    It is capable of storing pictures and metadata.
    """

    def create_folder(self, dir_name: str):
        pass

    def upload_file(self, file_path: str, data):
        """
        Uploads a file to the storage system.
        :param file_path: Path to the file to be uploaded.
        :param data: Data to be uploaded.
        """
        pass


class SeafileStorage(Storage):
    def __init__(
        self, username: str, password: str, server_url: str, library_name: str
    ):

        client = SeafileAPI(
            login_name=username,
            password=password,
            server_url=server_url,
        )
        client.auth()
        for repo in client.list_repos():
            if repo.name == library_name:
                self._repo = client.get_repo(repo.id)
                return

        self._repo = client.create_repo(library_name)
        if self._repo is None:
            raise Exception("Failed to create library")

    @override
    def create_folder(self, dir_path: str) -> str:
        """Creates storage for a user and returns the URL to access it."""

        self._repo.create_dir(dir_path)
        return quote(
            f"{self._repo.server_url}/library/{self._repo.repo_id}/{self._repo.name}{dir_path}"
        )
