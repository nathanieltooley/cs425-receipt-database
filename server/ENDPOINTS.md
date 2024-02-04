# Overview

## All Endpoints
- `/api/receipt/fetch_many_keys`
  - `GET`: [Fetch Many Keys](#fetch-many-keys)
- `/api/receipt/upload`
  - `POST`: [Receipt Upload](#upload)
- `/api/receipt/view/<file_key>`
  - `GET`: [View Receipt](#view-receipt)
- `/api/receipt/delete/<file_key>`
  - `GET`: [Delete Receipt](#delete)
- `/api/tag/fetch_all`
  - `GET`: [Fetch All](#fetch-all-tags)
- `/api/tag/add/<tag_name>`
  - `POST`: [Add Tag](#add)
- `/api/tag/fetch/<tag_id>`
  - `GET`: [Fetch Tag](#fetch-tag)
- `/api/tag/delete/<tag_id>`
  - `GET`: [Delete Tag](#delete-1)

## Responses
For more information about HTTP Responses 
see the [MDN Article](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status).

### Successful Responses
These responses indicate successful processing of the client's request.
These will be mentioned for each applicable endpoint 
with body / header format (if applicable),
but meaning will may not be elaborated on.
- **`200` - OK**
  - Successful processing of the request
  - Body contains requested or resulting resource.
- **`201` - Created**
  - Successfully created resource from request
  - Unclear when to use over `200`
- **`204` - No Content**
  - Successful processing of the request
  - Body is empty

### Client Error Responses
These responses indicate an issue with the client's request.
These will be mentioned for each applicable endpoint,
but meaning will may not be elaborated on.
- **`400` - Bad Request**
  - The request is missing required information or is formatted incorrectly.
- **`401` - Unauthorized (Unauthenticated)**
  - The request is missing or has invalid authentication required for this method
  - (Not Implemented)
- **`403` - Forbidden**
  - The request's authentication does not grant it access to the resource.
  - (Not Implemented)
- **`404` - Not Found**
  - The requested resource does not exist

### Server Error Responses
These responses indicated an issue on the server side that a client cannot fix themselves. 
- **`500` - Internal Server Error**
  - Generic error occurred while processing the request
  - Possible on any request
- **`501` - Not Implemented**
  - The functionality for this request has not been implemented yet
  - Will be stated per applicable endpoint
- **`507` - Insufficient Storage**
  - The connected file storage or database is out of space
  - Possible on any `POST` and `PUT` request

# Receipts
## Upload
Uploads a file to the system. 

- Endpoint: **`/api/receipt/upload`**
- Method: `POST`
- `POST` Data:
  - `file`
    - The file to be uploaded.
    - Filename will be used as key to fetch later.
      - Must be a valid filename for the file store being used.

### Responses
- **`200` - OK**
- ~~**`201` - Created**~~
  - Unclear when to use `200` vs `201`
- **`400` - Missing Key**
  - When an upload request does not specify a "file" key where the file is stored
- **`400` - Missing Filename**
  - When an upload request is sent without a filename
- **`400` - Missing File**
  - When an upload request is sent without a file

## View Receipt
Fetch a receipt's image.
- Endpoint: `/api/receipt/view/<file_key>`
  - `file_key`: The name of the key you wish to view
- Method `GET`

### Responses
- **`200` - OK**
  - Content-Type: Any
  - `Body` - The image of the requested receipt
- **`404` - No Such Key**
  - If the requested key is not found in the database

## Fetch Many Keys
Fetch all know receipt keys
- Endpoint: `/api/receipt/fetch_many_keys`
- Method: `GET`

### Responses
- **`200` - OK**
  - Content-Type: `text/html`
  - `Body`: `{"results":[<tag_id_1>, <tag_id_2>, ...]`
    - Array may be empty

## Delete
- Endpoint: `/api/receipt/delete/<file_key>`
  - `file_key`: The name of the key you wish to delete
- Method: `GET`
  - **Absolutely _should NOT_ be `GET`! Change to `DELETE` ASAP!**

### Responses
- **`204` - No Content** OR **`200` - OK**
  - Receipt existed and has been removed
- **`404` - Not Found**
  - Receipt does not exist
  - Means either:
    - Receipt already deleted
    - Incorrect Key


# Tags
## Add
- Endpoint:  `/api/tag/add/<tag_name>`
  - `tag_name`: The name of the tag you wish to create
- Method: `POST`
- `POST` Data:
  - None

### Responses
- **`200` - OK**
- **`400` - Missing Name**
  - When an upload request does not specify a tag name

## Fetch Tag
- Endpoint - `/api/tag/fetch/<int: tag_id>`
  - `tag_id`: Int id of the tag you wish to fetch
- Method: `GET`

### Responses
- **`400` - No Such Tag**
  - If the requested tag id is not found in the database

## Fetch All Tags
Fetch all tag ids and names
- Endpoint: `/api/tag/fetch_all`
- Method: `GET`

### Responses
- **`200` - OK**

## Delete
Delete the specified tag
- Endpoint - `/api/tag/delete/<int\:tag_id>`
  - `tag_id`: The int id of the key you wish to delete
- Method: `GET`
  - **Absolutely _should NOT_ be `GET`! Change to `DELETE` ASAP!**

### Responses
- **`204` - No Content** OR **`200` - OK**
  - Tag existed and has been removed
- **`404` - Not Found**
  - Tag does not exist
  - Means either:
    - Tag already deleted
    - Incorrect Key
