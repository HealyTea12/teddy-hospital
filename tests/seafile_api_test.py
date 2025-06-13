import anyio
import pytest
import toml

from backend.config import config
from backend.seafile import SeafileAPI


@pytest.mark.anyio
class TestSeafileAPI:
    @classmethod
    def setup_class(cls):
        config = toml.load("backend/config.toml")
        cls.client = SeafileAPI(
            account_token=config["storage"]["seafile"][0]["SEAFILE_ACCOUNT_TOKEN"],
            server_url=config["storage"]["seafile"][0]["SEAFILE_URL"],
        )
        cls.client.auth()
        cls.repo = cls.client.create_repo("test_repo")

    @classmethod
    def teardown_class(cls):
        # Cleanup code to run after each test
        cls.client.delete_repo(cls.repo.repo_id)

    def test_list_repos(self):
        repos = self.client.list_repos()

    def test_upload_file(self):
        self.repo.create_dir("/test_dir")
        self.repo.upload_file("/test_dir", "tests/img/eichhornchen.jpeg")
        assert True

    def test_upload_file_with_upload_link(self):
        self.repo.create_dir("/test_dir")
        upload_link = self.repo.create_shared_link("/test_dir", can_upload=True)
        self.repo.upload_file_via_upload_link(
            upload_link, "/", "tests/img/eichhornchen.jpeg"
        )
        assert True

    def test_upload_in_memory_file(self):
        import tempfile

        self.repo.create_dir("/test_dir")

        with tempfile.SpooledTemporaryFile() as f:
            f.write(b"test")
            f.seek(0)
            self.repo.upload_file("/test_dir", f)
            assert True

    async def test_upload_in_memory_file2(self):
        self.repo.create_dir("/test_dir")
        async with anyio.SpooledTemporaryFile() as f:
            await f.write(b"test")
            await f.seek(0)
            self.repo.upload_file("/test_dir", await f.read())
            assert True

    def test_get_shared_links_library(self):
        links = self.repo.get_shared_link_library()
        assert isinstance(links, list)

    def test_create_share_link(self):
        self.repo.create_dir("/test_dir")
        link = self.repo.create_shared_link("/test_dir", can_upload=True)
        assert link is not None
        sl = self.repo.get_shared_link_library()
        [l for l in sl if l.get("link") == link]
        assert len(sl) > 0

    # this test fails because the seafile api only returns 25 links instead of all.
    def test_create_many_links(self):
        for i in range(40):
            self.repo.create_dir(f"/test_dir_{i}")
            link = self.repo.create_shared_link(f"/test_dir_{i}", can_upload=True)
            assert link is not None
        sl = self.repo.get_shared_link_library()
        assert len(sl) >= 40
