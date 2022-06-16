FROM mongo

COPY init-products.json /init-products.json

CMD mongoimport --host mongo --db products -u root -p SuperSecret --collection products --type json --file /init-products.json --jsonArray