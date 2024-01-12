# Storage Hooks
This directory contains implemented storage hooks.
All modules (excluding `storage_hooks.py`) are expected to contain the following:
- A class inheriting `storage_hooks.StorageHook`
- A function called `init_script`
  - This function should be a script that sets up the storage hook
  - It is expected to be an interactive script, so user input is acceptable
  - It is expected to call `initialize_storage` on the storage hook at some point
  - While no arguments are passed, some may be added in the future

> None of this is set in stone and all of it is subject to change.

Additionally, `../configure.py` uses expects the module name to be match its possible arguments.
This may be later changed to search this directory for hooks.

There is no location for local storage of configuration, so that needs to be determined.
If using a hard coded directory, it should be a subdirectory of this project.
If using a directory that is not a subdirectory of this project, we should follow some standard 
(the [platformdirs](https://pypi.org/project/platformdirs/) project may be useful here).