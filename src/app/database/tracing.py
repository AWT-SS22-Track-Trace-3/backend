from json import dumps
import pymongo

from ..constants import *
from .init import client

# pymongo connecting to mongoDB
products = client["track-trace"]["products"]

# This DB is used to search products

class Tracing:

    def search(query):
        return dumps(list(products.find( query )))

    def getProduct(serial_number):
        return products.find_one({"serial_number": serial_number}, {'_id': 0})
