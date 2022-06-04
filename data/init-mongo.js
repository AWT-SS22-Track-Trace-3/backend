db = new Mongo().getDB("products");

db.createUser({
    user: 'root',
    pwd: 'SuperSecret',
    roles: [
        {
            role: 'readWrite',
            db: 'products',
        },
    ],
});

/*
db.auth("root", "SuperSecret");

db.createCollection('products', { capped: false });

var data = cat("./init-products.json");
var dataJSON = JSON.parse(data);

db.log.insertOne({ "message": JSON.stringify(dataJSON) });

db.products.insert(dataJSON.products);

*/