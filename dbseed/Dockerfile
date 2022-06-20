FROM mongo

COPY init-admin.json /init-admin.json

COPY init-products.json /init-products.json

CMD mongoimport --host mongo --db track-trace -u root -p SuperSecret --collection users --type json --file /init-admin.json --jsonArray && \
    mongoimport --host mongo --db track-trace -u root -p SuperSecret --collection products --type json --file /init-products.json --jsonArray