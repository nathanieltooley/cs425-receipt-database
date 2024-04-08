from urllib import parse

from sqlalchemy import create_engine

from configure import CONFIG, ManualRemoteSQLConfig, RemoteSQLConfig
from storage_hooks.storage_hooks import DatabaseHook


class RemoteSQL(DatabaseHook):
    """Arbitrary SQLAlchemy Connection"""

    @staticmethod
    def build_url(config: RemoteSQLConfig) -> str:
        # See https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
        engine_string = config.dialect
        if config.driver:
            engine_string += f"+{config.driver}"
        engine_string += "://"
        if config.username:
            engine_string += parse.quote_plus(config.username)
        if config.password:
            engine_string += f":{parse.quote_plus(config.password)}"
        if config.host or config.port:
            engine_string += "@"
            engine_string += config.host or ""
            if config.port:
                engine_string += f":{config.port}"
        if config.database is not None:
            engine_string += f"/{config.database}"
        return engine_string

    def __init__(self):
        super().__init__()
        self.config = CONFIG.RemoteSQL
        self.is_manual_url = isinstance(self.config, ManualRemoteSQLConfig)
        if self.is_manual_url:
            self.url = self.config.url
        else:
            self.url = self.build_url(self.config)
        self.engine = create_engine(self.url)

    def update_storage(self) -> bool:
        """Migrates a copy of the database to the current scheme version.

        Returns:
            True if successful, False otherwise.
        """
        raise NotImplementedError
