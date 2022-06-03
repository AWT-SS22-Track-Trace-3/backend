import pymongo
import time

from ..constants import *

# pymongo connecting to mongoDB
client = pymongo.MongoClient(
    host=MONGO['DOCKER'],
    port=MONGO['PORT'],
    username=MONGO['USERNAME'],
    password=MONGO['PASSWORD']
)
products = client["Tracking"]["products"]

class Tracking:

    def create_product(product, owner):
        document = { "product.serialNumber": product["serialNumber"] }

        if products.find_one( document ).count() == 0:
            entry = {
                "used": False,
                "history": [],
                "owner": [ owner ],
                "product": product
            }
            return products.insert_one(product)

        return { "message": "ERROR" }

    def checkout_product(product):
        document = { "product.serialNumber": product.serialNumber }
        projection = { "used": 1, "history.$.checkin": 1 }

        result = products.find_one( document, projection )

        if not result["used"] and result["checkin"]:
            update_history = {
                                "$push": {
                                    "history": {
                                        "$each": [
                                            {
                                                "timestamp_checkout": time.time(),
                                                "owner": product.owner,
                                                "future_owner": product.f_owner,
                                                "timestamp_checkin": None,
                                                "checkin": False
                                            }
                                        ],
                                        "$position": 0
                                    }
                                }
                            }

            return products.update_one( document, update_history )

        return None

    def checkin_product(product, owner):
        document = { "product.serialNumber": product.serialNumber }
        projection = { "used": 1, "history.$.checkin": 1 }

        result = products.find_one( document, projection )

        if not (result["used"] and result["checkin"]):
            update_history = {
                "$set": {
                    "history.$.timestamp_checkin": time.time(),
                    "history.$.checkin": True
                },
                "$push": {
                    "owner": owner
                }
            }
            
            return products.update_one( document, update_history )

        return None

    def terminate_product(serialNumber):
        document = { "product.serialNumber": serialNumber }
        projection = { "used": 1, "history.$.checkin": 1 }

        result = products.find_one( document, projection )

        if not result["used"] and result["checkin"]:
            return products.update_one( document, { "$set": { "used": True } } )

        return None
