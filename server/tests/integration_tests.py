import pytest
from storage_hooks.storage_hooks import DatabaseHook

from test_hooks import sqlite3, file_system, aws_s3


@pytest.fixture(params=[sqlite3])
def db_hook(request):
    hook: DatabaseHook = request.params()
    hook.initialize_storage()
    return db_hook


@pytest.fixture(params=[file_system, aws_s3])
def file_hook(request):
    return request.params()


@pytest.fixture()
def app(db_hook, file_hook):
    from app import create_app

    app = create_app(file_hook, db_hook)

    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app
