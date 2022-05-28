import pymongo

from ..common.constants import *

# pymongo connecting to mongoDB
client = pymongo.MongoClient(
    host=MONGO['DOCKER'],
    port=MONGO['PORT'],
    username=MONGO['USERNAME'],
    password=MONGO['PASSWORD']
)
products = client["Products"]["products"]

def getProduct(id):
    products.find_one( { "id": id } )

def postProduct(product):
    products.insert_one(product)
