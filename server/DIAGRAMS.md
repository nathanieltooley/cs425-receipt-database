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

    Tag o-- Receipt
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
