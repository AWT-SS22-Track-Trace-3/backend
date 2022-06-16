# Track&Trace Backend

Description...

## Startup

 `docker-compose up`

## API

`/token`

POST: {
 username: str
 password: str
}

Response: {
 access_token: str
 token_type: str
}

`test/{id}`

Header: {
 access_token: str
}

GET: {
 id: str
}

Response: {
 username: str
 password: str | None = None 
 company: str | None = None
 address: str | None = None
 access_lvl: int
}

`/is_username/{username}`

Header: {
 access_token: str
}

GET: {
 username: str
}

Response: {
 is_username: bool
}

`/signup`

Header: {
 access_token: str
}

POST: {
 username: str
 password: str
 company: str
 address: str
 access_lvl: int
}

Response: {
 is_username: bool
}

`/create`

Header: {
 access_token: str
}

POST: {
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

Response: None

`/checkout`

Header: {
 access_token: str
}

POST: {
 transaction_date: str
 shipment_date: str
 owner: str
 owner_address: str
 f_owner: str
 f_owner_address: str
}

Response: None


`/checkin`

Header: {
 access_token: str
}

POST: {
 transaction_date: str
 shipment_date: str
 prev_owner: str
 prev_owner_address: str
 owner: str
 owner_address: str
}

Response: None

`/terminate/{serial_number}`

Header: {
 access_token: str
}

GET: {
 serial_number: str
}

Response: None

## Database Setup

The Docker setup will automatically create a `products` database with a `products` collection in it.

For this collection, the user `(username: root, password: SuperSecret)` will be created and it will be filled with data by the `dbseed` service.

*Note:* To reset the database (**this will delete all data**), remove the Docker volume `backend_mongodata`. As long as this volume is present, initialization scripts will have no impact.

To force an image rebuild on docker compose, run:

`docker compose up --build`
