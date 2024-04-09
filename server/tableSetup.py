from receipt import Base
from storage_hooks.SQLite3 import SQLite3

hook = SQLite3()
Base.metadata.drop_all(hook.engine)
Base.metadata.create_all(hook.engine)
