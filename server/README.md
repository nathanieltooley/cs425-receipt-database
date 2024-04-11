# Receipt Database Back-End Server
Hosts API and puts data in configured storage.

## Setup
### Virtual Environment
It is recommend to use a virtual environment to avoid dependency issues.
```shell
# Create the virtual environment
python -m venv ./venv

# Activate the virtual environment
source venv/bin/activate  # macOS / Linux
venv\Scripts\actiate.bat  # Windows CMD
venv\Scripts\Activate.ps1 # Windows PowerShell
```
### Install Requirements
```shell
python -m pip install -r requirements.txt
```
> **Note:** Some requirements are only needed in some cases
> and may optionally be ignored. 
<details>
<summary>Conditional Requirements</summary>

- `black`
  - Used for code styling / formatting during development
- `pytest` and `pytest-mock`
  - Used for running tests
- `gunicorn`
  - "Included" production WSGI server (see [Running](#running))
- `boto3` and `botocore`
  - Used for AWS S3 connection
</details>

### Configure `config.json`
See [Configuration](#configuration)

### Initialize Hooks
The hooks need to be initialized to ensure proper operation.
```shell
python configure.py initialize <hook> [--clean]
```
Replace `<hook>` with `meta` for the database hook, `file` for the file hook, or `both` for both.
The `--clean` parameter will delete preexisting data in applicable locations if included.

## Running
For running in production, a Use a production WSGI server should be used.
[Gunicorn](https://gunicorn.org/) is included as a requirement for this purpose, 
but you may choose to use [another](https://flask.palletsprojects.com/en/2.3.x/deploying/).

Ensure your virtual environment is active if applicable.
```shell
gunicorn -w 4 'app:create_app()'
```

Gunicorn, by default, listens on `127.0.0.1:8000`. 
This will only listen to requests from the local host and on port 8000.
This can be changed with the `-b` argument. 
E.g. `-b 0.0.0.0:1234` to listen to any request to port 1234.
> Note: You may want to use a reverse proxy instead of setting Gunicorn to `0.0.0.0`.

## Configuration
Behavior is configured with the `config.json` file.
The current working directory is the checked first,
then the `Paperless` directory in the [user config directory](#user-directories).
If no config is found, uses defaults.

A template is provided as `config_template.json`. 
Any section may be omitted, 
but any present section must have all fields 
(unless explicitly labeled Optional).
<details>
<summary>Config Details</summary>

### Storage Hooks
This determines which hooks will be used.
- `file_hook`
  - Which hook to use to store the actual file.
  - `"AWS"` for AWS S3 (see [AWSS3](#awss3))
  - `"FS"` for local file system (see [FileSystem](#filesystem))
    - Default
- `meta_hook`
  - Which hook to use to store metadata
  - `"SQLite3"` for a SQLite3 database (see [SQLite3])
    - Default
  - `"RemoteSQL"` for any other SQLAlchemy compatible database (see [RemoteSQL](#remotesql))


### SQLite3
Can be also be done with RemoteSQL, but this also does file / directory creation. 
- `db_path`
  - The path to the SQLite database
  - Defaults to `receipts.sqlite3` in the [user data directory](#user-directories).

### RemoteSQL
This project uses [SQLAlchemy](https://www.sqlalchemy.org/) to work with databases,
therefore any database that [SQLAlchemy supports](https://docs.sqlalchemy.org/en/20/dialects/) can be used.
> Note: External dialects will need to be installed manually.
- `dialect`
  - The database engine 
  - e.g. `sqlite` or `postgres`
- `driver`
  - An alternative DBAPI to use
  - Optional
  - e.g. `pysqlite` or `aiosqlite`
- `username`
  - The username to sign in to the database
  - Optional*
- `password`
  - The password to sign in to the database
  - Optional*
- `host`
  - The hostname / IP address to connect to the database
  - Optional*
- `port`
  - The port the database listens on
  - Optional*
- `database`
  - The database within the DBMS to use
  - Optional
> Optional* - Will not error if absent. 
> May be required to actually connect to the database!

#### Manual RemoteSQL
With the above options, the database URL is [programmatically](https://docs.sqlalchemy.org/en/20/core/engines.html#creating-urls-programmatically).
Alternatively, you can manually provide the database url for SQLAlchemy.
See [Database URLs](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls).
- `url`
  - The URL to pass to SQLAlchemy to connect to the database.

### AWSS3
Blob data (the actual files) can be stored in an AWS S3 Bucket.
- `bucket_name`
  - The name of the AWS S3 Bucket to use
- `access_key_id`
  - The AWS access key id
  - Optional | Defaults to system environment
- `secret_access_key`
  - The AWS secret access key to use
  - Optional | Defaults to system environment

### FileSystem
Store files in a directory on the local system.
- `file_path`
  - The path to the directory to store the files
  - Defaults to the [user data directory](#user-directories)

</details>

## User Directories
We use [platformdirs](https://github.com/platformdirs/platformdirs) to select appropriate default directories.
The most likely locations are as follows:
- User Config Directory
  - macOS - `/Users/<username>/Library/Application Support/Paperless`
  - Windows - `C:\Users\<username>\AppData\Local\Papertrail\Paperless`
  - Linux - `/home/<username>/.config/Paperless`
- User Data Directory
  - macOS - `/Users/<username>/Library/Application Support/Paperless`
  - Windows - `C:\Users\<username>\AppData\Local\Papertrail\Paperless`
  - Linux - `/home/<username>/.local/share/Paperless`

## Development Guidelines
Python style guides follow [the Black code style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html).
Python docstrings follow [Google's Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
