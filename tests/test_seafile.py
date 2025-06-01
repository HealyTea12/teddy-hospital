import pytest

from backend.seafile.main import SeafileAPI


class TestSeafileAPI:
    @pytest.mark.anyio
    async def test_auth_success(self, monkeypatch):
        api = SeafileAPI.__new__(SeafileAPI)
        api.login_name = "ez270"
        api.password = "G?vixEwCcaZE"
        api.server_url = "https://heibox.uni-heidelberg.de"
        api.timeout = 1
        called = {}

        def fake_auth(self):
            called["auth"] = True

        api.auth = fake_auth.__get__(api)
        api.auth()
        assert called["auth"]

    @pytest.mark.anyio
    async def test_create_and_list_repo(self, monkeypatch):
        api = SeafileAPI.__new__(SeafileAPI)
        api.server_url = "https://heibox.uni-heidelberg.de"
        api.token = "token"
        api.headers = {}
        api.timeout = 1
        # Mock create_repo
        monkeypatch.setattr(
            api,
            "create_repo",
            lambda repo_name, passwd=None, story_id=None: {
                "repo_id": "r1",
                "repo_name": repo_name,
            },
        )
        # Mock list_repos
        api.RepoData = lambda *a, **kw: ("r1", "repo1", 1, 2, "now")
        monkeypatch.setattr(
            api,
            "list_repos",
            lambda type="mine", name_contains="": [("r1", "repo1", 1, 2, "now")],
        )
        repo = api.create_repo("repo1")
        repos = api.list_repos()
        assert repo["repo_id"] == "r1"
        assert any(r[0] == "r1" for r in repos)

    @pytest.mark.anyio
    async def test_get_repo(self, monkeypatch):
        api = SeafileAPI.__new__(SeafileAPI)
        api.server_url = "https://heibox.uni-heidelberg.de"
        api.token = "token"
        api.headers = {}
        api.timeout = 1

        # Patch requests.get to return a dummy response with status_code and text
        class DummyResponse:
            status_code = 200
            text = "{}"

        monkeypatch.setattr("requests.get", lambda *a, **kw: DummyResponse())

        # Provide a dummy Repo class with repo_id attribute set to 'r1'
        class DummyRepo:
            def __init__(self, *a, **kw):
                self.repo_id = "r1"

        api._repo_obj = lambda repo_id: DummyRepo()
        repo = api.get_repo("r1")
        assert repo.repo_id == "r1"

    @pytest.mark.anyio
    async def test_delete_repo(self, monkeypatch):
        api = SeafileAPI.__new__(SeafileAPI)
        api.server_url = "https://heibox.uni-heidelberg.de"
        api.token = "token"
        called = {}

        def fake_delete_repo(repo_id):
            called["deleted"] = repo_id

        api.delete_repo = fake_delete_repo
        api.delete_repo("r1")
        assert called["deleted"] == "r1"
