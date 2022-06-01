import pymongo
import time

from .common.constants import *

# pymongo connecting to mongoDB
client = pymongo.MongoClient(
    host=MONGO['DOCKER'],
    port=MONGO['PORT'],
    username=MONGO['USERNAME'],
    password=MONGO['PASSWORD']
)
products = client["Products"]["products"]

class DB:

    def getProduct(id):
        product = products.find_one( { "id": id } )

    def createProduct(auth, product):
        # authenticate vendor
        if auth:
            entry = {
                "used": False,
                "history": [],
                "product": product
            }
            products.insert_one(product)

    # at timestamp and vendor identification to transaction history
    def checkinProduct(id, owner_auth, owner, prev_owner):
        update_history = { "timestamp": time.time(), "checkout": True, "owner": prev_owner, "future_owner": owner, "checkin": True }
        products.update_one( { "id": id, "checkout": "not checkout" } )
        if id:
            return { "message": ""}

    def checkoutProduct(id, owner_auth, owner, f_owner):
        update_history = { "timestamp": time.time(), "checkout": True, "owner": owner, "future_owner": f_owner, "checkin": False }
        products.update_one( { "id": id, "checkout": "not checkout" } )

    def terminateProduct(id):
        products.update_one( { "id": id, "used": True } )
