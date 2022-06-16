# Track&Trace Backend

Description...

## Startup

 `docker-compose up`

## Database Setup

The Docker setup will automatically create a `products` database with a `products` collection in it.

For this collection, the user `(username: root, password: SuperSecret)` will be created and it will be filled with data by the `dbseed` service.

*Note:* To reset the database (**this will delete all data**), remove the Docker volume `backend_mongodata`. As long as this volume is present, initialization scripts will have no impact.

To force an image rebuild on docker compose, run:

`docker compose up --build`
