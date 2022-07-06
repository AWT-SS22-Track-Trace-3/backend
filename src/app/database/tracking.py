import pymongo
import time
from fastapi import HTTPException
from datetime import datetime

from ..constants import *
from .init import client

# pymongo connecting to mongoDB

products = client["track-trace"]["products"]

class Tracking:

    def create_product(product, user):
        document = { "serial_number": product["serial_number"] }

        if user["access_lvl"] > 3:
            owner = product["supplier"]["owner"]
        else:
            owner = user["username"]

        if products.find_one( document ) is None:
            entry = {
                "used": False,
                "reported": False,
                "supply_chain": [
                    {
                        "id": 0,
                        "transaction_date": datetime.fromisoformat(product["supplier"]["transaction_date"]),
                        "date_received": datetime.fromisoformat(product["supplier"]["shipment_date"]),
                        "checked_out": False,
                        "checked_in": True,
                        "owner": owner,
                        "future_owner": "",
                        "date_shipped": ""
                    }
                ]
            }

            for key, val in product.items():
                if key != "supplier" and key != "supply_chain":
                    entry[key] = val

            return products.insert_one(entry).acknowledged

        return False

    def checkout_product(self, product, username):
        target_product = products.find_one({
            "serial_number": product["product"]
        })

        next_index = len(target_product["supply_chain"])

        validate = self.validateProduct(target_product)
        if not validate:
            return {
                        "result": validate,
                        "chain_step": next_index - 1
                    }

        for item in target_product["supply_chain"]:
            if item.owner == username:
                if not item.checked_in:
                    #raise HTTPException(status_code=400, detail="Product was not previously checked out.")
                    return {
                        "result": validate,
                        "chain_step": next_index - 1
                    }

        document = { 
            "serial_number": product["product"],
            "$and": [
                { "supply_chain.checked_out": False },
                { "supply_chain.checked_in": True },
                { "supply_chain.owner": username}
            ]
        }
    
        update = {
            "$set": {
                "supply_chain.$.checked_out": True,
                "supply_chain.$.checkout_date": datetime.utcnow(),
                "supply_chain.$.future_owner": product["future_owner"],
                "date_shipped": product["shipment_date"]
            },
            "$push": {
                "supply_chain": {
                    "id": next_index,
                    "transaction_date": product["transaction_date"],
                    "checked_out": False,
                    "owner": username
                }
            }
        }

        return {"result": products.update_one( document, update ).acknowledged}

    def checkin_product(self, product, owner):
        target_product = products.find_one({
            "serial_number": product["product"]
        })

        next_index = len(target_product["supply_chain"])

        validate = self.validateProduct(target_product)
        if not validate:
            return {
                        "result": validate,
                        "chain_step": next_index - 1
                    }

        for item in target_product["supply_chain"]:
            if item.future_owner == owner["username"]:
                if not item.checked_out:
                    #raise HTTPException(status_code=400, detail="Product was not previously checked out.")
                    return {
                        "result": False,
                        "chain_step": next_index - 1
                    }

        query = { 
            "serial_number": product["product"],
            "$and": [
                { "supply_chain.checked_in": False },
                { "supply_chain.checked_out": False },
                { "supply_chain.owner": owner["username"] },
                { "supply_chain.transaction_date": product["transaction_date"] }
            ]
        }

        update = {
            "$set": {
                "supply_chain.$.checked_in": True,
                "supply_chain.$.date_received": product["shipment_date"],
                "supply_chain.$.checkin_date": datetime.utcnow()
            }
        }
            
        return {"result": products.update_one( query, update ).acknowledged}

    def terminate_product(serial_number):
        document = { "serial_number": serial_number }
        projection = { "used": 1, "history": 1 }

        result = products.find_one( document, projection )

        if result is not None and not result["used"] and result["history"][0]["checkin"]:
            return products.update_one( document, { "$set": { "used": True } } ).acknowledged

        return False
    
    def reportProduct(serial_number):
        products.update_one({"serial_number": serial_number}, {"reported": True})

    def validateProduct(product):
        if product is None:
            # raise HTTPException(status_code=400, detail="Product was not found.")
            return False

        if product is product["used"]:
            # raise HTTPException(status_code=400, detail="Product has been terminated.")
            return False

        if product is product["reported"]:
            # raise HTTPException(status_code=400, detail="Product is blocked for investigation.")
            return False

        return True