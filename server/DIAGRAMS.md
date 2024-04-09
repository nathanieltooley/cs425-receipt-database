# Diagrams
## Table of Contents
- [Entity relationship Diagram](#entity-relationship-diagram)
- [Class Diagram](#class-diagram)
- [Flow Chart](#flow-chart)
- [Sequence Diagrams](#sequence-diagrams)
- [Gantt Charts](#gantt-charts)

## Entity Relationship Diagram
```mermaid
erDiagram
    Tag {
        int id PK "autoincrement"
        string name
    }
    Receipt {
        int id PK "autoincrement"
        string name
        string storage_key
        datetime upload_dt "UTC"
    }
    receipt_tag {
        int tag_id PK, FK
        int receipt_id PK, FK
    }

    Receipt }o--|| receipt_tag: ""
    receipt_tag ||--o{ Tag: ""
```

## Class Diagram
```mermaid
classDiagram
    class Tag{
      id : int
      name : str
      export() dict
    }
    class Receipt{
      id : int
      name : name
      storage_key : str
      upload_dt : datetime
      tags : list[Tag]
      export() dict
    }
    
    class DatabaseHook {
        engine : sqlalchemy.Engine
        save_objects()
        delete_objects()
        create_receipt() Receipt
        fetch_recipt() Receipt
        fetch_receipts() list[Receipt]
        update_receipt() Receipt
        delete_receipt() int
        create_tag() Tag
        fetch_tag() Tag
        fetch_tags() list[Tag]
        update_tag() Tag
        delete_tag() int
        initialize_storage()
    }
    
    class MetaHook {
        _make_key() str$
        save() str*
        replace()*
        fetch() bytes*
        delete()*
        initialize_storage()*
    }
    
    class SQLite3 {
        config : _SQLite3Config
    }
    class AWSS3Hook {
        config : _AWSS3Config
        client : boto3.Client
        bucket_name : str
        _delete_all()
    }
    class FileSystemHook {
        config : _FileSystemConfig
        file_path : str
        _delete_all()
    }
    
    class _StorageHooks {
        file_hook : str
        meta_hook : str
        default()$ _StorageHooks
    }
    
    class _SQLite3Config {
        db_path : str
        default() _SQLite3Config$
    }
    class _FileSystemConfig {
        file_path : str
        default() _FileSystemConfig$
    }
    class _AWSS3Config {
        bucket_name : str
        access_key_id : str
        secret_access_key : str
        default() _AWSS3Config$
    }
    class _Config {
        StorageHooks : _StorageHooks
        SQLite3 : _SQLite3Config
        FileSystem : _FileSystemConfig
        AWSS3 : _AWSS3Config
        DEFAULT_FILE_PATH : str
        save()
        from_file()  _Config$
    }

    Tag o-- Receipt
    
    DatabaseHook ..|> SQLite3
    MetaHook ..|> AWSS3Hook
    MetaHook ..|> FileSystemHook
    
    SQLite3 *-- _SQLite3Config
    AWSS3Hook *-- _AWSS3Config
    FileSystemHook *-- _FileSystemConfig
    
    _StorageHooks --* _Config
    _SQLite3Config --* _Config
    _AWSS3Config --* _Config
    _FileSystemConfig --* _Config
```

## Flow Chart
```mermaid
flowchart LR
    Client[Flutter Client]
    API[Flask API]
    MetaHook[Metadata Hook]
    FileHook[File Hook]
    
    SQL[SQLAlchemy]
    SQLE[3rd Party SQLAlchemy Dialects]
    cMeta[Custom]
    
    FS[Local File System]
    AWS[AWS S3]
    cFile[Custom]

    Client <--> API
    API <--> MetaHook & FileHook
    MetaHook --- SQL & SQLE
    MetaHook -.- cMeta
    FileHook --- AWS & FS
    FileHook -.- cFile
```

## Sequence Diagrams
### Upload Receipt
```mermaid
sequenceDiagram
    API ->>+ Server : upload(receipt_data)
    Server ->>+ FileHook : upload(receipt_data.image)
    FileHook -->>- Server : storage_key
    Server ->>+ MetaHook : save(Receipt)
    MetaHook -->>- Server : Receipt
    Server -->>- API : json(Receipt)
```
### Fetch Receipt(s)
```mermaid
sequenceDiagram
    API ->>+ Server : fetch(receipt_id)
    Server ->>+ MetaHook : fetch(receipt_id)
    MetaHook -->>- Server : Receipt
    Server -->>- API : json(Receipt)
```

### View Receipt
```mermaid
sequenceDiagram
    API ->>+ Server : view(receipt_id)
    Server ->>+ MetaHook : fetch(receipt_id)
    MetaHook -->>- Server : Receipt
    Server ->>+ FileHook : fetch(receipt.storage_key)
    FileHook -->>- Server : Receipt Image
    Server -->>- API : Receipt Image
```

### Update Receipt
```mermaid
sequenceDiagram
    API ->>+ Server : upload(receipt_id, receipt_data)
    Server ->>+ MetaHook : update(receipt_data)
    MetaHook -->>- Server : Receipt
    Server ->>+ FileHook : replace(receipt_data.image)
    FileHook -->>- Server : 
    Server -->>- API : json(Receipt)
```

### Delete Receipt
```mermaid
sequenceDiagram
    API ->>+ Server : delete(receipt_id)
    Server ->>+ MetaHook : delete(receipt_id)
    MetaHook -->>- Server : storage_key
    Server ->>+ FileHook : delete(storage_key)
    FileHook -->>- Server : 
    Server -->>- API : 
```

### Create Tag
```mermaid
sequenceDiagram
    API ->>+ Server : create(tag_data)
    Server ->>+ MetaHook : create(tag_data)
    MetaHook -->>- Server: Tag
    Server -->>- API : json(Tag)
```

### Fetch Tag
```mermaid
sequenceDiagram
    API ->>+ Server : fetch(tag_id)
    Server ->>+ MetaHook : fetch(tag_id)
    MetaHook -->>- Server: Tag
    Server -->>- API : json(Tag)
```

### Update Tag
```mermaid
sequenceDiagram
    API ->>+ Server : update(tag_data)
    Server ->>+ MetaHook : update(tag_data)
    MetaHook -->>- Server: Tag
    Server -->>- API : json(Tag)
```

### Delete Tag
```mermaid
sequenceDiagram
    API ->>+ Server : delete(tag_id)
    Server ->>+ MetaHook : delete(tag_id)
    MetaHook -->>- Server: Tag
    Server -->>- API : json(Tag)
```

## Gantt Charts
### Original
```mermaid
gantt
    dateFormat YYYY-MM-DD
    axisFormat %m-%d
    tickInterval 2week
    weekday monday
    todayMarker off
    
    section Front End
        Create Receipt Dashboard    :2024-01-08, 2w
    
    section Back End
        Create Storage Setup(s)     :2024-01-08, 2w
        Create Remaining Endpoints  :2024-01-08, 2w
        Implement Storage Migrations:2024-01-22, 2w
        Create Docker Image         :2024-02-19, 2w
        
    section Full Stack
        Implement Users             :2024-01-22, 2w
        Add Tagging                 :2024-02-05, 2w
        Documentation               :2024-01-08, 8w
```

### Realized
```mermaid
gantt
    dateFormat YYYY-MM-DD
    axisFormat %m-%d
    tickInterval 2week
    weekday monday
    todayMarker off
    
    section Front End
        Create Receipt Dashboard    :2024-01-08, 2w
        Create Receipts Upload Button : 
        Create Basic Login/Sign Up Screen : 
        Make Dashboard Scrollable : 
        Add Cache : 
        Show Thumbnails on Dashboard : 
        Add Receipt Searching : 
        Update and Delete Receipts : 
        Add In-App Camera : 
    
    section Back End
        Create Storage Setup(s)     :2024-01-08, 2w
        Create Remaining Endpoints  :2024-01-08, 2w
        Save Custom Metadata : 
        Send Custom Metadata : 
        Create Fetch Many Endpoints : 
        Create Docker Image         :2024-02-19, 2w
        Create Testing Suite : 
        Add Config File : 
        
    section Full Stack
        
        Documentation               :2024-01-08, 8w
```

### Issues
```mermaid
gantt
    dateFormat YYYY-MM-DD
    
    Presentation Work	:2023-10-14, 2024-01-11
    Set up Flutter app	:2023-10-14, 2023-10-31
    Create a basic, empty home screen	:2023-10-14, 2023-10-24
    Create a button to upload receipts	:2023-10-14, 2023-10-24
    Create a dashboard to view receipts	:2023-10-14, 2024-01-11
    Setup db file(s) and file storage if necessary	:2023-10-14, 2024-02-20
    Process for converting older versions to newer versions	:2023-10-14
    Create a basic, login/sign up screen	:2023-10-14, 2023-10-30
    Set up Flask app	:2023-10-14, 2023-10-17
    Connect to a storage service	:2023-10-16, 2023-11-01
    Create GET Receipt endpoint	:2023-10-18, 2023-10-19
    Create POST Receipt endpoint	:2023-10-18, 2023-10-19
    Create GET Receipts endpoint	:2023-10-18, 2024-01-16
    Create POST Delete Receipt endpoint	:2023-10-18, 2023-10-21
    Upload a file using button	:2023-10-24, 2023-10-31
    Create React App Boilerplate	:2023-10-26, 2024-01-11
    Implement OAuth / SSO Login	:2023-10-26
    Add user receipt tagging	:2023-10-26, 2024-01-25
    Implement user tagging on S3 buckets	:2023-10-26, 2024-02-08
    `app.py` `view_receipt` raises exception	:2023-10-31, 2023-11-01
    Create scrollable region on dashboard	:2024-01-11, 2024-01-18
    API Endpoint for Multiple Images without Filenames	:2024-01-11, 2024-02-20
    Boto3 Upload Metadata	:2024-01-11, 2024-01-13
    Store Receipt Metadata	:2024-01-11, 2024-01-13
    Add metadata to upload	:2024-01-11, 2024-02-20
    Create Cache File	:2024-01-11, 2024-01-18
    Edit View Receipt endpoint to avoid temp files	:2024-01-12, 2024-01-12
    Create Receipt Holders	:2024-01-16
    Add Receipt Thumbnails	:2024-01-25, 2024-02-29
    Add ability to add custom tags to receipts	:2024-01-25, 2024-02-15
    Create Search Bar	:2024-01-25, 2024-02-01
    AWS S3 No Key Found error when attempting to view receipt known to exist	:2024-02-13, 2024-02-27
    Return receipt ID from upload_receipt endpoint	:2024-02-13, 2024-02-13
    Add update (`PUT`) methods for tags and receipts	:2024-02-13, 2024-02-26
    Create testing suite	:2024-02-13, 2024-02-23
    Create a way to initilize the database	:2024-02-13, 2024-02-16
    Somehow handle a deleted image	:2024-02-13, 2024-02-20
    Add sorting to requests	:2024-02-15, 2024-02-15
    Add GitHub actions for linting, testing, and formatting	:2024-02-15, 2024-02-27
    Add configuration for AWS S3	:2024-02-16, 2024-02-26
    Fix up layout of frontend dashboard	:2024-02-27, 2024-02-29
    Use Camera in App	:2024-02-29
    [Stretch] User Accounts	:2024-02-29
    [Stretch] OCR	:2024-02-29
    Allow Update and Delete of Receipts and Tags	:2024-02-29, 2024-03-26
    Upload receipt doesn't save bytes	:2024-03-12, 2024-03-12
    Empty Receipt Name	:2024-03-12, 2024-03-26
    Make API Domain / Port More Flexible	:2024-03-26
```