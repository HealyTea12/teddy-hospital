import toml

# Change relative import to absolute import
from .storage import SeafileStorage, Storage


class Config:
    storage: list[Storage]
    debug: bool = False
    results_per_image: int

    def __init__(self, config_file: str):
        self.config_file = config_file
        config = toml.load(config_file)
        self.storage = []
        for s in config.get("storage", {}).get("seafile", []):
            self.storage.append(
                SeafileStorage(
                    username=s.get("SEAFILE_USERNAME"),
                    password=s.get("SEAFILE_PASSWORD"),
                    repo_token=s.get("SEAFILE_REPO_TOKEN"),
                    account_token=s.get("SEAFILE_ACCOUNT_TOKEN"),
                    server_url=s.get("SEAFILE_URL"),
                    library_name=s.get("SEAFILE_LIBRARY_NAME"),
                )
            )
        self.debug = config.get("DEBUG", False)
        self.carrousel_size = config.get("CARROUSEL_SIZE", 10)
        self.results_per_image = config.get("RESULTS_PER_IMAGE", 1)
        self.animal_types = config.get("ANIMAL_TYPES", [])
        self.animal_types.append("other")

        security = config.get("security", {})
        self.password_hash = security.get("PASSWORD_HASH", "")
        self.access_token_expire_time = security.get("ACCESS_TOKEN_EXPIRE_TIME", 30)
        self.secret_key = security.get("SECRET_KEY", "")
        self.algorithm = security.get("ALGORITHM", "HS256")
        self.timezone = security.get("TIMEZONE", "")


import pathlib

CONFIG_PATH = pathlib.Path(__file__).parent / "config.toml"
config = Config(str(CONFIG_PATH))
