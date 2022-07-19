from datetime import datetime
from inspect import formatannotationrelativeto
from pycountry import countries
from pydantic import BaseModel
from typing import Any
from dateutil import parser
from dateutil.relativedelta import *
import pymongo
from enum import Enum

from ..routers.authentication import User
from ..constants import *
from .models.models import Incident, IncidentFilter
from .init import client
from .tracking import Tracking
from ..helpers.incident_grouping import IncidentGrouping
from ..helpers.pagination import Pagination
from ..helpers.incidentAggregation import IncidentAggregator

# pymongo connecting to mongoDB
incidents = client["track-trace"]["incidents"]

# this database persisist security incidents in the supply chain


class Incidents():

    def report(incident: Incident):
        Tracking.reportProduct(incident["product"])

        return incidents.insert_one(incident).acknowledged

    def heatmap_data():
        heatmap = []
        for c in countries:
            addresses = []
            for f in incidents.find({"user.country": c.alpha_2}, {"_id": 0, "user.address": 1}):
                addresses.append(f["user"]["address"])
            heatmap.append({c.alpha_2: incidents.count_documents({"user.country": c.alpha_2}),
                            "addresses": addresses
                            })

        return heatmap

    def getGroupedIncidents(country, group, sort, pagination: Pagination = None):
        aggregator = IncidentAggregator("incidents", "products", "users")

        aggregation = [
            {
                '$match': {
                    "_id": {
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

        if(country != "all"):
            aggregation = aggregator.getByCountry(country)

            grouping = IncidentGrouping(group, sort)

            aggregation = aggregation + grouping.getQuery()
        else:
            aggregation = aggregator.getCountryIncidences()

        if pagination is not None:
            aggregation = aggregation + pagination.getQuery()

        print(aggregation)
        # print(list(incidents.aggregate(aggregation)))

        return list(incidents.aggregate(aggregation))

    def getIncidents(country, filter, pagination: Pagination = None):
        aggregator = IncidentAggregator("incidents", "products", "users")

        if filter is not None:
            filter_type = FilterTypes[filter["filter_type"]].value
        else:
            filter_type = "all"

        if filter_type == FilterTypes.date.value:
            interval = filter["interval"]
            start_date = parser.parse(filter["filter_value"], ignoretz=True)
            end_date = parser.parse(filter["filter_value"], ignoretz=True)

            if interval == "day":
                end_date += relativedelta(days=+1)
            elif interval == "month":
                end_date += relativedelta(months=+1)
            elif interval == "year":
                end_date += relativedelta(years=+1)
            else:
                return None

            aggregation = aggregator.getByCountryAndTimerange(
                country, start_date, end_date)

        elif filter_type == FilterTypes.incident_type.value:
            aggregation = aggregator.getByCountryAndType(
                country, filter["filter_value"])

        elif filter_type == FilterTypes.company_name.value:
            aggregation = aggregator.getByCountryAndCompany(
                country, filter["filter_value"])
        else:
            aggregation = aggregator.getByCountry(country)

        if pagination is not None:
            aggregation = aggregation + pagination.getQuery()

        # print(aggregation)
        # print(list(incidents.aggregate(aggregation)))

        return(list(incidents.aggregate(aggregation)))


class FilterTypes(Enum):
    date = "date"
    incident_type = "incident_type"
    company_name = "name"
