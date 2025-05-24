import anyio
import pytest

from backend.seafile import SeafileAPI


@pytest.mark.anyio
class TestSeafileAPI:
    @classmethod
    def setup_class(cls):
        cls.client = SeafileAPI(
            login_name="ez270",
            password="G?vixEwCcaZE",
            server_url="https://heibox.uni-heidelberg.de",
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
            self.repo.upload_file("/test_dir", f.fileno())
            assert True

    async def test_upload_in_memory_file2(self):

        self.repo.create_dir("/test_dir")
        async with anyio.SpooledTemporaryFile() as f:
            await f.write(b"test")
            await f.seek(0)
            self.repo.upload_file("/test_dir", f.wrapped.fileno())
            assert True
