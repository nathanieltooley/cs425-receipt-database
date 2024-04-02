# Diagrams
## Overview
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
      +int id
      +str name
      +dict export()
    }
    class Receipt{
      +int id
      +str name
      +str storage_key
      +datetime upload_dt
      +list[Tag] tags
      +dict export()
    }
    
    class DatabaseHook {
        Engine engine
        save_objects()
        delete_objects()
        create_receipt()
        fetch_recipt()
        fetch_receipts()
        update_receipt()
        delete_receipt()
        create_tag()
        fetch_tag()
        fetch_tags()
        update_tag()
        delete_tag()
        initialize_storage()
    }
    
    class MetaHook {
        _make_key()
        save()
        replace()
        fetch()
        delete()
        initialize_storage()
    }
    
    class SQLite3 {
        config
    }
    class AWSS3Hook {
        config
        client
        bucket_name
        _delete_all()
    }
    class FileSystemHook {
        config
        file_path
        _delete_all()
    }
    
    class _StorageHooks {
        file_hook
        meta_hook
        default()
    }
    
    class _SQLite3Config {
        str db_path
        default()
    }
    class _FileSystemConfig {
        str file_path()
        default()
    }
    class _AWSS3Config {
        bucket_name
        access_key_id
        secret_access_key
        default()
    }
    class _Config {
        StorageHooks
        SQLite3
        FileSystem
        AWSS3
        DEFAULT_FILE_PATH
        save()
        from_file()
    }

    Tag o-- Receipt
    
    DatabaseHook <|-- SQLite3
    MetaHook <|-- AWSS3Hook
    MetaHook <|-- FileSystemHook
    
    SQLite3 *-- _SQLite3Config
    AWSS3Hook *-- _AWSS3Config
    FileSystemHook *-- _FileSystemConfig
    
    _StorageHooks --* _Config
    _SQLite3Config --* _Config
    _AWSS3Config --* _Config
    _FileSystemConfig --* _Config
```

## Flow
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

## Sequence
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
