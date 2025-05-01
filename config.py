import toml

# Change relative import to absolute import
from storage import SeafileStorage, Storage


class Config:
    storage: list[Storage]
    debug: bool = False

    def __init__(self, config_file: str):
        self.config_file = config_file
        config = toml.load(config_file)
        self.storage = []
        for s in config.get("storage", {}).get("seafile", []):
            self.storage.append(
                SeafileStorage(
                    s.get("SEAFILE_USERNAME"),
                    s.get("SEAFILE_PASSWORD"),
                    s.get("SEAFILE_URL"),
                    s.get("SEAFILE_LIBRARY_NAME"),
                )
            )
        self.debug = config.get("DEBUG", False)


config = Config("config.toml")
