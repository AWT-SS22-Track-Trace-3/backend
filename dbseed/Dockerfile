FROM mongo

COPY users.json /users.json
COPY incidents.json /incidents.json
COPY products.json /products.json

CMD mongoimport --host mongo --db track-trace -u root -p SuperSecret --collection users --type json --file /users.json --jsonArray && \
    mongoimport --host mongo --db track-trace -u root -p SuperSecret --collection products --type json --file /products.json --jsonArray && \
    mongoimport --host mongo --db track-trace -u root -p SuperSecret --collection incidents --type json --file /incidents.json --jsonArray