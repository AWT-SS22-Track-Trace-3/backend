from json import dumps
import pymongo

from ..constants import *

# pymongo connecting to mongoDB
client = pymongo.MongoClient(
    host=MONGO['DOCKER'],
    port=MONGO['PORT'],
    username=MONGO['USERNAME'],
    password=MONGO['PASSWORD']
)
products = client["track-trace"]["products"]

# This DB is used to search products

class Tracing:

    def search(query):
        return dumps(list(products.find( query )))
