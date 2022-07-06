from json import dumps
import pymongo

from ..constants import *
from .init import client

# pymongo connecting to mongoDB
products = client["track-trace"]["products"]

# This DB is used to search products

class Tracing:

    def search(query):
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

    def getProduct(serial_number):
        aggregation = [
            {
                "$match": {
                    "serial_number": serial_number
                },
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
                "$unwind": "$supply_chain"
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "supply_chain.owner",
                    "foreignField": "username",
                    "as": "supply_chain.owner"
                }
            },
            {
                "$unwind": "$supply_chain.owner"
            },
            {
                "$project": {
                    "supply_chain.owner._id": 0,
                    "supply_chain.owner.password": 0,
                    "supply_chain.owner.access_lvl": 0,
                }
            },
            {
                "$group": {
                    "_id": "$_id",
                    "supply_chain": { "$push": "$supply_chain" }
                }
            },
            {
                "$lookup": {
                    "from": "products",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "product"
                }
            },
            {
                "$unwind": "$product"
            },
            {
                "$addFields": {
                    'product.supply_chain': '$supply_chain'
                }
            },
            {
                "$replaceRoot": {
                    "newRoot": "$product"
                }
            },
            {
                "$project": {
                    "_id": 0
                }
            }
        ]

        #print(list(products.aggregate(aggregation)))
        
        return list(products.aggregate(aggregation))[0]
