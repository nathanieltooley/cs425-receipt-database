from sqlalchemy import URL, create_engine

from configure import CONFIG, ManualRemoteSQLConfig, RemoteSQLConfig
from storage_hooks.storage_hooks import DatabaseHook


class RemoteSQL(DatabaseHook):
    """Arbitrary SQLAlchemy Connection"""

    @staticmethod
    def build_url(config: RemoteSQLConfig) -> URL:
        # See https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
        engine_string = URL(
            config.dialect + (f"+{config.driver}" if config.driver else ""),
            username=config.username,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database,
            query=None,
        )
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
