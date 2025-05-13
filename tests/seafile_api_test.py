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

    def tearDown(self):
        # Cleanup code to run after each test
        pass

    def test_list_repos(self):
        repos = self.client.list_repos()


if __name__ == "__main__":
    unittest.main()
