from datetime import datetime
from pycountry import countries
from pydantic import BaseModel
from typing import Any
import pymongo

from ..routers.authentication import User
from ..constants import *
from .models.models import Incident
from .init import client
from .tracking import Tracking
from ..helpers.incident_grouping import IncidentGrouping
from ..helpers.pagination import Pagination

# pymongo connecting to mongoDB
incidents = client["track-trace"]["incidents"]

# this database persisist security incidents in the supply chain

class Incidents():

    def report(incident: Incident):
        Tracking.reportProduct(incident["product"])

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
    
    def getIncidents(country, group, sort, pagination: Pagination = None):
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
                    "as": "product"
                }
            },
            {
                "$unwind": "$product"
            },
            {
                "$addFields": {
                    "reported_at": {
                        "$arrayElemAt": ["$product.supply_chain", "$chain_step"]
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

        if country == "all":
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
                            "assigned_company.address.country": country
                        }
                    },
                    {
                        "$lookup": {
                            "from": "users",
                            "localField": "product.manufacturers",
                            "foreignField": "username",
                            "as": "product.manufacturers"
                        }
                    },
                    {
                        "$project": {
                            "reported_at": 0,
                            "product._id": 0,
                            "product.manufacturers._id": 0,
                            "product.manufacturers.password": 0,
                            "product.manufacturers.access_lvl": 0,
                            "assigned_company._id": 0,
                            "assigned_company.password": 0,
                            "assigned_company.access_lvl": 0
                        }
                    }
                ]
        
        if(group is not None and country != "all"):
            grouping = IncidentGrouping(group, sort)

            aggregation = aggregation + grouping.getQuery()

        if pagination is not None:
            aggregation = aggregation + pagination.getQuery()
        
        print(aggregation)
        #print(list(incidents.aggregate(aggregation)))

        return list(incidents.aggregate(aggregation))
    
    def getGroupedIncidents(scope, group, sort, pagination = None):
        pass