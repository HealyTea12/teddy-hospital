import json
import os
from typing import NamedTuple

import requests
from anyio import SpooledTemporaryFile
from fastapi import params
from pydantic import ValidatorFunctionWrapHandler
from seafileapi.exceptions import ClientHttpError
from seafileapi.utils import urljoin


def parse_response(response: requests.Response):
    if response.status_code >= 400:
        raise ConnectionError(response.status_code, response.text)
    else:

        data = json.loads(response.text)
        return data


class Repo(object):

    def __init__(self, token, server_url, repo_id, by_api_token=True):

        self.server_url = server_url
        self.token = token
        self.repo_id = repo_id
        self.timeout = 30
        self.headers = {}
        self._by_api_token = by_api_token

        self.auth()
        r = self.get_repo_details()
        self.name = r.get("repo_name")

    def auth(self):

        self.headers = {
            "accept": "application/json",
            "Authorization": "Bearer " + self.token,
        }

    def _repo_info_url(self):
        if self._by_api_token:
            return f"{self.server_url}/api/v2.1/via-repo-token/repo-info/"

        return f"{self.server_url}/api/v2.1/repos/{self.repo_id}/"

    def _repo_dir_url(self):
        if self._by_api_token:
            return f"{self.server_url}/api/v2.1/via-repo-token/dir/"
        return f"{self.server_url}/api2/repos/{self.repo_id}/dir/"

    def _repo_file_url(self):
        if self._by_api_token:
            return f"{self.server_url}/api/v2.1/via-repo-token/file/"

        return f"{self.server_url}/api/v2.1/repos/{self.repo_id}/file/"

    def _repo_upload_link_url(self):
        if self._by_api_token:
            return "%s/%s" % (
                self.server_url.rstrip("/"),
                "api/v2.1/via-repo-token/upload-link/",
            )

        return "%s/%s" % (
            self.server_url.rstrip("/"),
            "api2/repos/%s/upload-link/" % self.repo_id,
        )

    def _repo_download_link_url(self):
        if self._by_api_token:
            return "%s/%s" % (
                self.server_url.rstrip("/"),
                "api/v2.1/via-repo-token/download-link/",
            )

        return "%s/%s" % (
            self.server_url.rstrip("/"),
            "api2/repos/%s/file/" % self.repo_id,
        )

    def get_repo_details(self):
        url = self._repo_info_url()
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        repo = parse_response(response)
        return {
            "repo_id": repo.get("repo_id"),
            "repo_name": repo.get("repo_name"),
            "size": repo.get("size"),
            "file_count": repo.get("file_count"),
            "last_modified": repo.get("last_modified"),
        }

    def list_dir(self, dir_path="/") -> list[dict[str, str]]:
        url = self._repo_dir_url()
        if self._by_api_token:
            params = {"path": dir_path}
        else:
            params = {"p": dir_path}
        response = requests.get(
            url, params=params, headers=self.headers, timeout=self.timeout
        )
        resp = parse_response(response)
        return resp

    def create_dir(self, path: str):
        url = self._repo_dir_url()
        params = {"p": path} if not self._by_api_token else {"path": path}
        payload = '-----011000010111000001101001\r\nContent-Disposition: form-data; name="operation"\r\n\r\nmkdir\r\n-----011000010111000001101001--'

        response = requests.post(
            url,
            params=params,
            data=payload,
            headers=self.headers
            | {
                "Content-Type": "multipart/form-data; boundary=---011000010111000001101001"
            },
            timeout=self.timeout,
        )
        return parse_response(response)

    def rename_dir(self, path, newname):
        url = self._repo_dir_url()
        params = {"path": path} if "/api/v2.1/via-repo-token" in url else {"p": path}
        data = {"operation": "rename", "newname": newname}
        response = requests.post(
            url, params=params, json=data, headers=self.headers, timeout=self.timeout
        )
        return parse_response(response)

    def delete_dir(self, path):
        url = self._repo_dir_url()
        params = {"path": path} if "/via-repo-token" in url else {"p": path}
        response = requests.delete(
            url, params=params, headers=self.headers, timeout=self.timeout
        )
        return parse_response(response)

    def get_file(self, path):
        # /api2/repos/{repo_id}/file/detail/
        url = (
            self._repo_file_url()
            if "/via-repo-token" in self._repo_file_url()
            else urljoin(self.server_url, "api2/repos/%s/file/detail/" % self.repo_id)
        )
        params = {"path": path} if "/via-repo-token" in url else {"p": path}
        response = requests.get(
            url, params=params, headers=self.headers, timeout=self.timeout
        )
        return parse_response(response)

    def create_file(self, path):
        url = self._repo_file_url()
        params = {"path": path} if "/via-repo-token" in url else {"p": path}
        data = {"operation": "create"}
        response = requests.post(
            url, params=params, json=data, headers=self.headers, timeout=self.timeout
        )
        return parse_response(response)

    def rename_file(self, path, newname):
        """
        Rename a file
        :param path: file path
        :param newname:file newname
        :return:
        """
        url = self._repo_file_url()
        params = {"path": path} if "/via-repo-token" in url else {"p": path}
        data = {"operation": "rename", "newname": newname}
        response = requests.post(
            url, params=params, json=data, headers=self.headers, timeout=self.timeout
        )
        return parse_response(response)

    def delete_file(self, path):
        """
        Delete a file/folder
        :param p: file/folder path
        :return:{'success': True, 'commit_id': '2147035976f20495fdc0a85f1a8a9c109b22c97d'}
        """
        url = self._repo_file_url()
        params = {"path": path} if "/via-repo-token" in url else {"p": path}
        response = requests.delete(
            url, params=params, headers=self.headers, timeout=self.timeout
        )
        return parse_response(response)

    def upload_file(self, parent_dir, file_path):
        upload_link_url = self._repo_upload_link_url()
        params = (
            {"path": parent_dir}
            if "/via-repo-token" in upload_link_url
            else {"p": parent_dir}
        )
        response = requests.get(
            upload_link_url, params=params, headers=self.headers, timeout=self.timeout
        )
        upload_link = response.text.strip('"')
        upload_link = "%s?ret-json=1" % upload_link
        files = {"file": open(file_path, "rb")}
        data = {"parent_dir": parent_dir}
        response = requests.post(upload_link, files=files, data=data)
        if response.status_code == 200:
            return response.json()[0]
        else:
            raise Exception("upload file error")

    def download_file(self, file_path, save_path):
        url = self._repo_download_link_url()
        params = {"path": file_path} if "/via-repo-token" in url else {"p": file_path}
        response = requests.get(url, params=params, headers=self.headers)

        file_download_url = response.json()
        response = requests.get(file_download_url, headers=self.headers)

        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
        else:
            raise Exception("download file error")

    def create_shared_link(
        self,
        path: str,
        password: str | None = None,
        expire_days: int | None = None,
        can_edit: bool = False,
        can_download: bool = True,
        can_upload: bool = False,
    ) -> str:
        # first check if a link already exists with the corresponding permissions because otherwise seafile complains
        links = self.get_shared_links(path)
        for link in links:
            if (
                link["is_expired"] == False
                and link["permissions"]["can_edit"] == can_edit
                and link["permissions"]["can_download"] == can_download
                and link["permissions"]["can_upload"] == can_upload
            ):
                return link["link"]
            else:
                # couldn't find a way of updating the permissions, have to delete and create a new one
                self.delete_shared_link(link["token"])
        # TODO: with repo token
        url = f"{self.server_url}/api/v2.1/share-links/"
        payload = {
            "permissions": {
                "can_edit": can_edit,
                "can_download": can_download,
                "can_upload": can_upload,
            },
            "path": path,
            "repo_id": self.repo_id,
        }
        if password is not None:
            payload["password"] = password
        if expire_days is not None:
            payload["expire_days"] = expire_days
        headers = {"accept": "application/json", "content-type": "application/json"}
        response = requests.post(url, json=payload, headers=self.headers | headers)

        link = parse_response(response)["link"]
        return link

    def get_shared_links(self, path: str):
        url = f"{self.server_url}/api/v2.1/share-links/?repo_id={self.repo_id}&path={path}"
        response = requests.get(url, headers=self.headers)
        return parse_response(response)

    def delete_shared_link(self, token: str):

        url = f"{self.server_url}/api/v2.1/share-links/{token}/"
        headers = {"accept": "application/json"}
        response = requests.delete(url, headers=headers | self.headers)
        parse_response(response)

    def upload_file_via_upload_link(self, upload_link: str, dir_path: str, file_path):
        # get parent dir from upload link kind of dumb, but there is no other way except remembering
        # the path when creating the upload link
        url = f"{self.server_url}/api/v2.1/share-links/"
        r = requests.get(url, headers=self.headers, params={"repo_id": self.repo_id})
        for link in r.json():
            if link["link"] == upload_link:
                base_dir_path: str = link["path"]
                break
        shared_link_token = upload_link.split("/")[-2]
        url = f"{self.server_url}/api/v2.1/share-links/{shared_link_token}/upload/"
        params = {"path": dir_path}
        r = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        upload_link = r.json().get("upload_link")
        upload_link = "%s?ret-json=1" % upload_link
        files = {"file": open(file_path, "rb")}
        data = {"parent_dir": f"{base_dir_path.rstrip('/')}{dir_path}"}
        response = requests.post(upload_link, files=files, data=data)
        if response.status_code == 200:
            return response.json()[0]
        else:
            raise Exception("upload file error")


class SeafileAPI(object):

    def __init__(
        self, login_name: str, password: str, server_url: str, timeout: int = 30
    ):
        self.login_name = login_name
        self.username = None
        self.password = password
        self.server_url = server_url.strip().strip("/")
        self.token = None
        self.timeout = timeout

        self.headers = None

    def auth(self):
        data = {
            "username": self.login_name,
            "password": self.password,
        }
        url = f"{self.server_url}/api2/auth-token/"
        res = requests.post(url, data=data, timeout=self.timeout)
        if res.status_code != 200:
            raise ClientHttpError(res.status_code, res.content)
        token = res.json()["token"]
        assert len(token) == 40, "The length of seahub api auth token should be 40"
        self.token = token
        res = requests.get(f"{self.server_url}/api2/server-info/", timeout=self.timeout)
        if res.status_code != 200:
            raise ClientHttpError(res.status_code, res.content)

        # see comment at https://seafile-api.readme.io/reference/authentication
        if json.loads(res.text).get("version").startswith("11."):
            self.headers = {
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json",
            }
        else:
            self.headers = {
                "Authorization": "Token " + token,
                "Content-Type": "application/json",
            }

    def _repo_obj(self, repo_id):
        repo = Repo(self.token, self.server_url, repo_id, by_api_token=False)

        return repo

    class RepoData(NamedTuple):
        type: str
        id: str
        owner: str
        owner_name: str
        owner_contact_email: str
        name: str
        mtime: int
        modifier_email: str
        modifier_contact_email: str
        modifier_name: str
        mtime_relative: str  # TODO actually a datetime would be better
        size: int
        size_formatted: str
        encrypted: bool
        permission: str  # eg: rw
        virtual: bool
        root: str
        head_commit_id: str
        version: int
        salt: str
        groupid: str | None = None

    def list_repos(self, type: str = "mine", name_contains: str = "") -> list[RepoData]:
        """
        type: mine | shared | group | org
        """

        url = f"{self.server_url}/api2/repos"
        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
            params={
                "type": type,
                "nameContains": name_contains,
            },
        )
        return [SeafileAPI.RepoData(**p) for p in parse_response(response)]

    def get_repo(self, repo_id: str) -> Repo:
        url = f"{self.server_url}/api2/repos/{repo_id}"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        data = parse_response(response)
        repo_id = data.get("id")
        return self._repo_obj(repo_id)

    def create_repo(self, repo_name, passwd=None, story_id=None):
        url = urljoin(self.server_url, "api2/repos/")
        data = {
            "name": repo_name,
        }
        if passwd:
            data["passwd"] = passwd
        if story_id:
            data["story_id"] = story_id
        response = requests.post(
            url, json=data, headers=self.headers, timeout=self.timeout
        )
        if response.status_code == 200:
            data = parse_response(response)
            repo_id = data.get("repo_id")
            return self._repo_obj(repo_id)

    def delete_repo(self, repo_id):
        """Remove this repo. Only the repo owner can do this"""
        url = urljoin(self.server_url, "/api2/repos/%s/" % repo_id)
        requests.delete(url, headers=self.headers, timeout=self.timeout)
        return True
