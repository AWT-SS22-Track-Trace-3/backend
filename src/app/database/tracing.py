from json import dumps
import pymongo

from app.helpers.productAggregation import ProductAggregator

from ..constants import *
from .init import client

# pymongo connecting to mongoDB
products = client["track-trace"]["products"]

# This DB is used to search products


class Tracing:

    def search(query):
        print(query)
        aggregation = [
            {
                "$match": query
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "manufacturers",
                    "foreignField": "username",
                    "as": "manufacturers"
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "sellers",
                    "foreignField": "username",
                    "as": "sellers"
                }
            },
            {
                "$project": {
                    "manufacturers._id": 0,
                    "manufacturers.password": 0,
                    "manufacturers.access_lvl": 0,
                    "sellers._id": 0,
                    "sellers.password": 0,
                    "sellers.access_lvl": 0,
                    "_id": 0,
                }
            },
        ]

        return list(products.aggregate(aggregation))

    def defined_search(query, username):
        aggregator = ProductAggregator()

        aggregation = aggregator.getProductBySearchRestricted(query, username)

        result = list(products.aggregate(aggregation))

        if len(result) == 0:
            return []
        else:
            for product in result:
                product = Tracing._reverseCutSupplyChain(product, username)

        return result

    def getProduct(serial_number):
        aggregator = ProductAggregator()

        aggregation = (aggregator.getProductBySerial(serial_number))

        result = list(products.aggregate(aggregation))

        print(aggregation, result)

        if len(result) == 1:
            return Tracing._mergeSupplyChain(result[0])
        elif len(result) > 1:
            return False
        elif len(result) < 1:
            return []

    def getRestrictedProduct(serial_number, username):
        aggregator = ProductAggregator()

        aggregation = (aggregator.getProductBySerial(serial_number))

        result = list(products.aggregate(aggregation))

        #print(aggregation, result)

        if len(result) == 1:
            return Tracing._mergeSupplyChain(Tracing._reverseCutSupplyChain(result[0], username))
            #return Tracing._reverseCutSupplyChain(Tracing._mergeSupplyChain(result[0]), username)
        elif len(result) > 1:
            return False
        elif len(result) < 1:
            return []

    def _mergeSupplyChain(product):
        if len(product["incidents"]) > 0 and "type" in product["incidents"][0]:
            for incident in product["incidents"]:
                for index, item in enumerate(product["supply_chain"]):
                    if item["type"] != "incident" and item["id"] == incident["chain_step"]:
                        incident_item = incident
                        incident_item["incident_type"] = incident["type"]
                        incident_item["type"] = "incident"
                        product["supply_chain"].insert(
                            index + 1, incident_item)
        return product

    def _reverseCutSupplyChain(product, username):
        while product["supply_chain"]:
            if product["supply_chain"][-1]["owner"]["username"] == username:
                break
            else:
                product["supply_chain"].pop()

        return product
