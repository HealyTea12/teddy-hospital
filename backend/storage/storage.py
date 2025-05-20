from abc import ABC, abstractmethod
from typing import override
from urllib.parse import quote

import requests

from ..seafile import SeafileAPI


class Storage(ABC):
    """
    Base class for storage systems.
    It is capable of storing pictures and metadata.
    """

    @abstractmethod
    def create_storage_for_user(self, user_id: int) -> str:
        """
        Creates storage for a user and returns the URL to access it.
        :param user_id: ID of the user.
        :return: URL to access the storage.
        """
        pass

    @abstractmethod
    def upload_file(self, user_id: int | str, type: str, file_path: str | bytes):
        """
        Uploads a file to the storage system.
        :param user_id: ID of the user if int or upload link if str.
        :param type: Type of the file normal | xray.
        :param file_path: Path to the file to be uploaded. Or bytes if the file is in memory.
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
        assert self._repo is not None, "Failed to create library"
        if self._repo is None:
            raise Exception("Failed to create library")

    @override
    def create_storage_for_user(self, user_id: int) -> str:

        self._repo.create_dir(f"/{user_id}")
        return self._repo.create_shared_link(f"/{user_id}")

    @override
    def upload_file(self, user_id: int | str, type: str, file_path: str | bytes):
        """
        Uploads a file to the storage system.
        :param user_id: ID of the user.
        :param type: Type of the file normal | xray.
        :param file_path: Path to the file to be uploaded.
        """
        if isinstance(user_id, int) and isinstance(file_path, str):
            path = f"/{user_id}/{type}/{file_path.split('/')[-1]}"
            self._repo.upload_file(path, file_path)
