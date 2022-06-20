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

    def get_product(serialNumber):
        return products.find_one( { "product.serialNumber": serialNumber } )
