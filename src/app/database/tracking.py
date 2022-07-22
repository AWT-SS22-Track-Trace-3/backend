from itertools import chain
import pymongo
import time
from fastapi import HTTPException
from datetime import datetime
from dateutil.parser import isoparse

from ..constants import *
from .init import client

# pymongo connecting to mongoDB

products = client["track-trace"]["products"]


class Tracking:

    def create_product(product, user):
        document = {"serial_number": product["serial_number"]}

        if user["access_lvl"] > 3:
            owner = product["supplier"]["owner"]
        else:
            owner = user["username"]

        if products.find_one(document) is None:
            entry = {
                "used": False,
                "reported": False,
                "supply_chain": [
                    {
                        "id": 0,
                        "type": "change_of_ownership",
                        "transaction_date": isoparse(product["supplier"]["transaction_date"]).date(),
                        "checkin_date": isoparse(product["supplier"]["transaction_date"]),
                        "checked_out": False,
                        "checked_in": True,
                        "owner": owner,
                        "future_owner": ""
                    }
                ]
            }

            for key, val in product.items():
                if key != "supplier" and key != "supply_chain":
                    entry[key] = val

            return products.insert_one(entry).acknowledged

        return False

    def checkout_product(serial_number, product, username):
        target_product = products.find_one({
            "serial_number": serial_number
        })

        next_index = len(target_product["supply_chain"])

        validate = Tracking.validateProduct(target_product)
        if not validate:
            return {
                "result": validate,
                "chain_step": next_index - 1
            }

        print(target_product)

        for item in target_product["supply_chain"]:
            if item.get("owner") == username:
                if not item.get("checked_in"):
                    #raise HTTPException(status_code=400, detail="Product was not previously checked out.")
                    return {
                        "result": validate,
                        "chain_step": next_index - 1
                    }

        new_supply_chain: list = target_product["supply_chain"]

        for chain_step in new_supply_chain:
            if not chain_step.get("checked_out") and chain_step.get("checked_in") and chain_step.get("owner") == username:
                chain_step["checked_out"] = True
                chain_step["checkout_date"] = datetime.utcnow()
                chain_step["future_owner"] = product["future_owner"]

        new_supply_chain += [
            {
                "id": next_index,
                "type": "shipment",
                "shipment_method": product["shipment"]["shipment_method"],
                "tracking_number": product["shipment"]["tracking_number"],
                "date_shipped": isoparse(product["shipment"]["date"]),
                "owner": product["shipment"]["handler"]
            },
            {
                "id": next_index + 1,
                "type": "change_of_ownership",
                "transaction_date": isoparse(product["transaction_date"]).date(),
                "owner": product["future_owner"],
                "checked_in": False,
                "checked_out": False
            }
        ]

        # print(new_supply_chain)

        return {"result": products.update_one({"serial_number": serial_number}, {
            "$set": {
                "supply_chain": new_supply_chain
            }
        }).acknowledged}

    def checkin_product(serial_number, product, username):
        target_product = products.find_one({
            "serial_number": serial_number
        })

        next_index = len(target_product["supply_chain"])

        validate = Tracking.validateProduct(target_product)
        if not validate:
            return {
                "result": validate,
                "chain_step": next_index - 1
            }

        for item in target_product["supply_chain"]:
            if item.get("future_owner") == username:
                if not item.get("checked_out"):
                    #raise HTTPException(status_code=400, detail="Product was not previously checked out.")
                    return {
                        "result": False,
                        "chain_step": next_index - 1
                    }

        updated_supply_chain = target_product["supply_chain"]

        for item in updated_supply_chain:
            if (item["type"] == "change_of_ownership"
                and not item.get("checked_in")
                and not item.get("checked_out")
                    and item.get("owner") == username
                    and item.get("transaction_date").date() == isoparse(product["transaction_date"]).date()):

                item["checked_in"] = True
                item["checkin_date"] = datetime.utcnow()

            if item["type"] == "shipment" and item["id"] == next_index - 2:
                item["date_delivered"] = isoparse(product["shipment_date"])

        return {"result": products.update_one({"serial_number": serial_number}, {
            "$set": {
                "supply_chain": updated_supply_chain
            }
        }).acknowledged}

    def terminate_product(serial_number):
        document = {"serial_number": serial_number}
        projection = {"used": 1, "history": 1}

        result = products.find_one(document, projection)

        if result is not None and not result["used"] and result["history"][0]["checkin"]:
            return products.update_one(document, {"$set": {"used": True}}).acknowledged

        return False

    def reportProduct(serial_number):
        products.update_one(
            {"serial_number": serial_number}, {"reported": True})

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
