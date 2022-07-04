from datetime import datetime
from pycountry import countries
from pydantic import BaseModel
from typing import Any
import pymongo

from ..routers.authentication import User
from ..constants import *
from .models.models import Incident
from .init import client

# pymongo connecting to mongoDB
incidents = client["track-trace"]["incidents"]

# this database persisist security incidents in the supply chain

class Incidents():

    def report(incident: Incident):
        return incidents.insert_one(incident).acknowledged

    def heatmap_data():
        heatmap = [ ]
        for c in countries:
            addresses = [ ]
            for f in incidents.find({ "user.country": c.alpha_2 }, { "_id": 0, "user.address": 1 }):
                addresses.append(f["user"]["address"])
            heatmap.append( { c.alpha_2: incidents.count_documents({ "user.country": c.alpha_2 }),
            "addresses": addresses
            } )

        return heatmap
    
    def getIncidents(scope):
        aggregation = [
            {
                '$match': { 
                    "_id" : {
                        "$exists": True
                    }
                }
            },
            {
                "$lookup": {
                    "from": "products",
                    "localField": "product",
                    "foreignField": "serial_number",
                    "as": "product_lookup"
                }
            },
            {
                "$unwind": "$product_lookup"
            },
            {
                "$addFields": {
                    "reported_at": {
                        "$arrayElemAt": ["$product_lookup.supply_chain", 0]
                    }
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "reported_at.owner",
                    "foreignField": "username",
                    "as": "assigned_company"
                }
            },
            {
                "$unwind": "$assigned_company"
            }
        ]

        if scope == "country":
            aggregation.append(
                {
                    "$group": {
                        "_id": "$assigned_company.address.country",
                        "count": {
                            "$sum": 1
                        }
                    }
                }
            )
        else:
            aggregation = aggregation + [
                    {
                        "$match": {
                            "assigned_company.address.country": scope
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "product_lookup": 0,
                            "reported_at": 0,
                            "assigned_company._id": 0,
                            "assigned_company.password": 0,
                            "assigned_company.access_lvl": 0
                        }
                    }
                ]
            

        return list(incidents.aggregate(aggregation))