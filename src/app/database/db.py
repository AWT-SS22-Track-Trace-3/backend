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
    product = products.find_one( { "id": id } )

def postProduct(auth, product):
    # authenticate vendor
    if auth:
        products.insert_one(product)

def checkinProduct(id):
    products.update_one( { "id": id, "checkout": "not checkout" } )
    if id:
        return { "message": ""}

def checkoutProduct(id):
    products.update_one( { "id": id, "checkout": "not checkout" } )

def terminateProduct(id):
    products.update_one( { "id": id, "checkout": "terminated" } )
