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
