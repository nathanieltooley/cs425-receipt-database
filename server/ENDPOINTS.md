# Overview

## All Endpoints
- Receipts
  - `/api/receipt/`
    - `GET`: [Fetch Receipts](#fetch-receipts)
  - `/api/receipt/`
    - `POST`: [Upload Receipt](#upload-receipt)
  - `/api/receipt/<id>/`
    - `GET`: [Fetch Receipt]
  - `/api/receipt/<id>/image`
    - `GET`: [View Receipt](#view-receipt)
  - `/api/receipt/<id>/`
    - `DELETE`: [Delete Receipt](#delete-receipt)
- Tags
  - `/api/tag/`
    - `GET`: [Fetch Tags](#fetch-tags)
  - `/api/tag/`
    - `POST`: [Add Tag](#add-tag)
  - `/api/tag/<id>`
    - `GET`: [Fetch Tag](#fetch-tag)
  - `/api/tag/<id>`
    - `DELETE`: [Delete Tag](#delete-tag)

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

### Common JSON Objects
These JSON structures are sent in multiple places.
> Note: Any array / list (here and elsewhere) may be empty!
#### Receipt JSON
```json5
{
    "id": <id>,  // Integer
    "name": <name>,  // String
    "upload_dt": <upload_dt>,  // UTC, "%Y-%m-%d %H:%M:%S"
    "tags": [<tag_id>, ...],  // List of Integer
}
```
#### Tag JSON
```json5
{
    "id": <id>,  // Integer
    "name": <name>,  // String
}
```

# Receipts
## Upload Receipt
Uploads a file to the system. 

- Endpoint: **`/api/receipt/`**
- Method: `POST`
- `POST` Data:
  - `file`
    - The file to be uploaded.
    - Filename will be used as key to fetch later.
      - Must be a valid filename for the file store being used.
  - `name`
    - A user-friendly name for the receipt.
    - May be non-unique
  - `tag`
    - The id for a tag to apply to the receipt
    - Can be repeated for any number of (existing) tags

### Responses
- **`200` - OK**
  - Content-Type: `text/json`
  - Body: `<Receipt JSON>`
- **`400` - Missing Key**
  - When an upload request does not specify a "file" key where the file is stored
- **`400` - Missing Filename**
  - When an upload request is sent without a filename
- **`400` - Missing File**
  - When an upload request is sent without a file

## View Receipt
Fetch a receipt's image.
- Endpoint: `/api/receipt/<id>/image/`
  - `id`: The id of the receipt you wish to view the image of
- Method `GET`

### Responses
- **`200` - OK**
  - Content-Type: Any
  - `Body` - The image of the requested receipt
- **`404` - No Such Key**
  - If the requested key is not found in the database

## Fetch Receipt
Fetch data of one receipt 
- Endpoint: `/api/receipt/<id>/`
  - `id`: The id of the receipt you wish to fetch
- Method: `GET`

### Responses
- **`200` - OK**
  - Content-Type: `text/json`
  - Body: `<Receipt JSON>`

## Fetch Receipts
Fetch all know receipt keys
- Endpoint: `/api/receipt/`
- Method: `GET`

### Responses
- **`200` - OK**
  - Content-Type: `text/json`
  - Body: `[<Receipt JSON>, ...]`

## Delete Receipt
- Endpoint: `/api/receipt/<id>`
  - `id`: The id of the receipt you wish to delete
- Method: `DELETE`

### Responses
- **`204` - No Content**
  - Receipt existed and has been removed
- **`404` - Not Found**
  - Receipt does not exist
  - Means either:
    - Receipt already deleted
    - Incorrect Key


# Tags
## Add Tag
- Endpoint:  `/api/tag/`
- Method: `POST`
- `POST` Data:
  - `name`
    - A user-friendly name for the tag
    - May be non-unique

### Responses
- **`200` - OK**
  - Content-Type: `text/json`
  - Body: `<Tag JSON>`
- **`400` - Missing Name**
  - When an upload request does not specify a tag name

## Fetch Tag
- Endpoint - `/api/tag/<id>`
  - `tag_id`: Int id of the tag you wish to fetch
- Method: `GET`

### Responses
- **`200` - OK**
  - Content-Type: `text/json`
  - Body: `<Tag JSON>`
- **`404` - No Such Tag**
  - If the requested tag id is not found in the database

## Fetch Tags
Fetch all tag ids and names
- Endpoint: `/api/tag/`
- Method: `GET`

### Responses
- **`200` - OK**
  - Content-Type: `text/json`
  - Body: `[<Tag JSON>, ...]`

## Delete Tag
Delete the specified tag
- Endpoint - `/api/tag/<id>`
  - `id`: The int id of the key you wish to delete
- Method: `DELETE`

### Responses
- **`204` - No Content**
  - Tag existed and has been removed
- **`404` - Not Found**
  - Tag does not exist
  - Means either:
    - Tag already deleted
    - Incorrect Key
