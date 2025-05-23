import unittest

from backend.seafile import SeafileAPI


class TestSeafileAPI(unittest.TestCase):

    def setUp(self):
        self.client = SeafileAPI(
            login_name="ez270",
            password="G?vixEwCcaZE",
            server_url="https://heibox.uni-heidelberg.de",
        )
        self.client.auth()
        self.repo = self.client.create_repo("test_repo")

    def tearDown(self):
        # Cleanup code to run after each test
        self.client.delete_repo(self.repo.repo_id)

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


if __name__ == "__main__":
    unittest.main()
