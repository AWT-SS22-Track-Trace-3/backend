# Track&Trace Backend

Description...

## Startup

 `docker-compose up`

## API

### Definition - access_lvl
- 0: Wholesaler, can checkin, checkout, and view associated products
- 1: Consumer, can checkin, terminate, and view associated products
- 2: Manufacturer, can create, checkout, and view associated products
- 3: Authorities, can signup users and view everything
- 4: Admin, has admin access


### Authentication

#### `/token`

- generates session token

POST (x-www-form-urlencoded): 
```
{
 username: str
 password: str
}
```

Response: 
```json
{  
 access_token: str
 token_type: str
 access_lvl: int
}
```


### Incidents

#### `/incident``

- enpoint to report an incident manually
- access_lvl: all

Header:
```json
{
 access_token: str  
}
```

POST:
```json
{
 type: str
 product: {
    name: str
    common_name: Any
    form: str
    strength: str
    drug_code: Any
    pack_size: int
    pack_type: Any
    serial_number: str
    reimbursment_number: Any
    containers: Any
    batch_number: str
    expiry_date: str
    coding: Any
    marketed_states: Any
    manufacturer_name: Any
    manufacturer_adress: Any
    marketing_holder_name: Any
    marketing_holder_adress: Any
    wholesaler: Any
 }
}
```

Response:
```json
{
 acknowledged: bool
}
```


#### `/heatmap``

- returns data for incident heatmap for countries worldwide
- access_lvl: 3 & 4

Header:
```json
{
 access_token: str
}
```

GET: 
```json
{ }
```

Response:
```json
{
 heatmap_data: [ …, { "DE": int }, … ]
}
```


### Login

#### `/is_username/{username}`

- checks if username exists
- access_lvl: 3 & 4

Header:
```json
{
 access_token: str
}
```

GET:
```json
{
 username: str
}
```

Response:
```json
{
 is_username: bool
}
```


### `/signup`

- signups new user
- access_lvl: 3 & 4

Header:
```json
{
 access_token: str  
}
```

POST:
```json
{
 username: str
 password: str
 company: str
 country: str
 address: str
 access_lvl: int
}
```

Response:
```json
{
 acknowledged: bool
}
```


### Tracing

#### `/search``

- returns results of POSTed search
- access_lvl: 3 & 4

Header:
```json
{
 access_token: str
}
```

POST:
```json
{
 MongoDB_query
}
```

Response:
```json
{
 MongoDB_result
}
```


### Tracking

#### `/create`

- inserts new product into database
- access_lvl: 2 & 4

Header:
```json
{
 access_token: str
}
```

POST:
```json
{
 name: str
 common_name: Any
 form: str
 strength: str
 drug_code: Any
 pack_size: int
 pack_type: Any
 serial_number: str
 reimbursment_number: Any
 containers: Any
 batch_number: str
 expiry_date: str
 coding: Any
 marketed_states: Any
 manufacturer_name: Any
 manufacturer_adress: Any
 marketing_holder_name: Any
 marketing_holder_adress: Any
 wholesaler: Any
}
```

Response:
```json
{
 acknowledged: bool
}
```


#### `/checkout`

- updates product history to "in transport to…"
- access_lvl: 0, 2, & 4

Header:
```json
{
 access_token: str
}
```

POST:
```json
{
 serial_number: str
 transaction_date: str
 shipment_date: str
 owner: str
 owner_address: str
 f_owner: str
 f_owner_address: str
}
```

Response:
```json
{
 acknowledged: bool
}
```


#### `/checkin`

- updates product history to "arrived at…"
- access_lvl: 0, 1, & 4

Header:
```json
{
 access_token: str
}
```

POST:
```json
{
 serial_number: str
 transaction_date: str
 shipment_date: str
 prev_owner: str
 prev_owner_address: str
 owner: str
 owner_address: str
}
```

Response:
```json
{
 acknowledged: bool
}
```


#### `/terminate`

- updates product history to "has been used"
- access_lvl: 1 & 4

Header:
```json
{
 access_token: str
}
```

POST:
```json
{
 serial_number: str
}
```

Response:
```json
{
 acknowledged: bool
}
```


### Default

#### `/test/{id}`

- testing endpoint, modify as you please

Header:
```json
{
 access_token: str
}
```

GET: 
```json
{
 id: str
}
```

Response:
```json
{
 username: str
 password: str | None = None 
 company: str | None = None
 address: str | None = None
 access_lvl: int
}
```


## Database Setup

The Docker setup will automatically create a `products` database with a `products` collection in it.

For this collection, the user `(username: root, password: SuperSecret)` will be created and it will be filled with data by the `dbseed` service.

*Note:* To reset the database (**this will delete all data**), remove the Docker volume `backend_mongodata`. As long as this volume is present, initialization scripts will have no impact.

To force an image rebuild on docker compose, run:

`docker compose up --build`
