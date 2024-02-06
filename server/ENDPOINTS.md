# Receipts
## Upload (POST)
Full endpoint - **/api/receipt/upload**

### Usage
Send a POST request that contains a _file_ key where the file you wish to upload is stored. This file must have a valid filename.

### User Errors
**Missing Key - 200**: When an upload request does not specify a "file" key where the file is stored
**Missing Filename - 400**: When an upload request is sent without a filename
**Missing File - 400**: When an upload request is sent without a file

## View Receipt (GET)
Full endpoint - **/api/receipt/view/<file_key>**, where file_key is the name of the key you wish to view

### Usage
Send a GET request to the **/api/receipt/view** endpoint and specify a file_key. This key is the key that represents the file in the DB.

### User Errors
**No Such Key - 400**: If the requested key is not found in the database

## Fetch Many Keys (GET)
Full endpoint - **/api/receipt/fetch_many_keys**

### Usage
Send a GET request. Currently returns all known keys inside the database.

## Delete (GET)
Full endpoint - **/api/receipt/delete/<file_key>**, where file_key is the name of the key you wish to delete

### Usage
Send a GET request to the **/api/receipt/delete/** endpoint and specify a file_key. This key is the key that represents the file in the DB.

# Tags
## Add (POST)
Full endpoint - **/api/tag/**

### Usage
Send POST request to the endpoint, specifying the "name=<tag_name>" in the POST data.

### User Errors
**Missing Name - 400**: When an upload request does not specify a tag name

## Fetch Tag (GET)
Full endpoint - **/api/tag/<int\:tag_id>**, where tag_id is int id of the tag you wish to fetch

### Usage
Send a GET request to the **/api/tag/** endpoint and specify a tag_id. This is the id that represents the tag in the DB.

### User Errors
**No Such Tag - 400**: If the requested tag id is not found in the database

## Fetch All Tags (GET)
Full endpoint - **/api/tag/**

### Usage
Send a GET request. Currently returns all known tags inside the database.

## Delete (DELETE)
Full endpoint - **/api/tag/<int\:tag_id>**, where tag_id is the int id of the key you wish to delete

### Usage
Send a GET request to the **/api/tag/** endpoint and specify a tag_id. This is the id that represents the tag in the DB.
