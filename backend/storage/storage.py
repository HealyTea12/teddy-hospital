import json
import os
from abc import ABC, abstractmethod
from curses.ascii import isdigit
from typing import IO, override
from urllib.parse import quote

import requests
from anyio import SpooledTemporaryFile

from ..seafile import Repo, SeafileAPI


class Storage(ABC):
    """
    Base class for storage systems.
    It is capable of storing pictures and metadata.
    """

    @abstractmethod
    def create_storage_for_user(self) -> str:
        """
        Creates storage for a user and returns the URL to access it.
        :param user_id: ID of the user.
        :return: URL to access the storage.
        """
        pass

    @abstractmethod
    def upload_file(self, user_id: int | str, type: str, file_path: os.PathLike | IO):
        """
        Uploads a file to the storage system.
        :param user_id: ID of the user if int or upload link if str.
        :param type: Type of the file normal | xray.
        :param file_path: Path to the file to be uploaded. Or bytes if the file is in memory.
        """
        pass


class SeafileStorage(Storage):
    def __init__(
        self,
        server_url: str,
        library_name: str,
        username: str | None = None,
        password: str | None = None,
        account_token: str | None = None,
        repo_token: str | None = None,
    ):
        self._id: int = 0
        if not (username and password) and not account_token and not repo_token:
            raise ValueError(
                "You must provide either: username and password or account token or repo token"
            )
        if username and password:
            client = SeafileAPI(
                login_name=username,
                password=password,
                server_url=server_url,
            )
            client.auth()
            for repo in client.list_repos():
                if repo.name == library_name:
                    self._repo = client.get_repo(repo.id)
            if self._repo is None:
                self._repo = client.create_repo(library_name)
            assert self._repo is not None, "Failed to create library"
        elif account_token:
            client = SeafileAPI(
                account_token=account_token,
                server_url=server_url,
            )
            client.auth()
            for repo in client.list_repos():
                if repo.name == library_name:
                    self._repo = client.get_repo(repo.id)
            if self._repo is None:
                self._repo = client.create_repo(library_name)
        elif repo_token:
            self._repo = Repo(
                server_url=server_url,
                token=repo_token,
                by_api_token=True,
            )
            # version 11 doesn't have the necessary endpoints for it to work with repo_token
            if int(self._repo.version.split(".")[0]) < 12:
                raise ValueError(
                    "Seafile version less than 12 do not support the necessary endpoints for the application to work, please use account token or username and password."
                )

        assert self._repo is not None  # for the type checker

        # Calculate the highest Id that is already there
        dirs = self._repo.list_dir("/")
        for d in dirs:
            if (d_name := d.get("name", "")).isdigit():
                self._id = max(self._id, int(d_name))
        self._id += 1

    @override
    def create_storage_for_user(self) -> str:
        self._repo.create_dir(f"/{self._id}")
        self._repo.create_dir(f"/{self._id}/normal")
        self._repo.create_dir(f"/{self._id}/xray")
        self._id += 1
        # We give upload permission so that we can use the QR code to upload the images later.
        # I don't like this solution because it gives people the opportunity to fill up storage with trash.
        return self._repo.create_shared_link(f"/{self._id-1}", can_upload=True)

    @override
    def upload_file(self, user_ref: int | str, type: str, file_path: os.PathLike | IO):
        """
        Uploads a file to the storage system.
        :param user_ref: either the number corresponding to the users storage or the upload link.
        :param type: Type of the file ('normal' | 'xray').
        :param file_path: Path or file descriptor to the file to be uploaded.
        """
        if isinstance(user_ref, int):
            path = f"/{user_ref}/{type}"
            self._repo.upload_file(path, file_path)
        elif isinstance(user_ref, str):
            self._repo.upload_file_via_upload_link(
                user_ref, f"/{type}", file_path, "image"
            )
