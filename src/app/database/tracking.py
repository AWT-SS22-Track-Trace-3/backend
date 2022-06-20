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
products = client["track-trace"]["products"]

class Tracking:

    def create_product(product, owner):
        document = { "product.serial_number": product["serial_number"] }

        if products.find_one( document ) is None:
            entry = {
                "used": False,
                "history": [
                    {
                        "timestamp_checkin": time.time(),
                        "checkin": True
                    }
                ],
                "owner": [ owner ],
                "product": product
            }
            return products.insert_one(entry).acknowledged

        return False

    def checkout_product(product):
        document = { "product.serial_number": product["serial_number"] }
        projection = { "used": 1, "history": 1 }

        result = products.find_one( document, projection )

        if result is not None and not result["used"] and result["history"][0]["checkin"]:
            update_history = {
                                "$push": {
                                    "history": {
                                        "$each": [
                                            {
                                                "timestamp_checkout": time.time(),
                                                "owner": product["owner"],
                                                "future_owner": product["f_owner"],
                                                "timestamp_checkin": None,
                                                "checkin": False
                                            }
                                        ],
                                        "$position": 0
                                    }
                                }
                            }

            return products.update_one( document, update_history ).acknowledged

        return False

    def checkin_product(product, owner):
        document = { "product.serial_number": product["serial_number"] }
        projection = { "used": 1, "history": 1 }

        result = products.find_one( document, projection )

        if result is not None and not result["used"] and not result["history"][0]["checkin"]:
            update_history = {
                "$set": {
                    "history.0.timestamp_checkin": time.time(),
                    "history.0.checkin": True
                },
                "$push": {
                    "owner": owner
                }
            }
            
            return products.update_one( document, update_history ).acknowledged

        return False

    def terminate_product(serial_number):
        document = { "product.serial_number": serial_number }
        projection = { "used": 1, "history": 1 }

        result = products.find_one( document, projection )

        if result is not None and not result["used"] and result["history"][0]["checkin"]:
            return products.update_one( document, { "$set": { "used": True } } ).acknowledged

        return False
