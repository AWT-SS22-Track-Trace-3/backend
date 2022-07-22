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
            #aggregation = aggregator.getByCountry(country)

            grouping = IncidentGrouping(group, sort, True)

            #aggregation = aggregation + grouping.getQuery()
            aggregation = aggregator.getCountrySummary(
                country, grouping.getQuery())

        else:
            aggregation = aggregator.getCountryIncidences()

        if pagination is not None:
            aggregation = aggregation + pagination.getQuery()

        # print(aggregation)
        # print(list(incidents.aggregate(aggregation)))
        result = list(incidents.aggregate(aggregation))

        #print(group, result)

        if group == "day" and country != "all":
            for item in result:
                date = datetime(item["_id"]["year"], 1, 1) + \
                    relativedelta(days=+item["_id"]["day"] - 1)
                item["_id"]["formatted"] = date.strftime("%d.%m.%Y")
                item["_id"]["raw"] = date.isoformat() + "Z"
        elif group == "month" and country != "all":
            for item in result:
                date = datetime(item["_id"]["year"], 1, 1) + \
                    relativedelta(months=+item["_id"]["month"] - 1)
                item["_id"]["formatted"] = date.strftime("%b %Y")
                item["_id"]["raw"] = date.isoformat() + "Z"

        return result

    def getIncidents(country, filter_type, filter_value, pagination: Pagination = None):
        aggregator = IncidentAggregator("incidents", "products", "users")

        if filter_type is not None and filter_value is not None:
            filter_type = FilterTypes[filter_type].value
        else:
            filter_type = "all"

        if filter_type == FilterTypes.day.value:
            start_date = parser.parse(filter_value)
            end_date = start_date + relativedelta(days=+1)

            aggregation = aggregator.getByCountryAndTimerange(
                country, start_date, end_date)

        elif filter_type == FilterTypes.day.value:
            start_date = parser.parse(filter_value)
            end_date = start_date + relativedelta(months=+1)

            aggregation = aggregator.getByCountryAndTimerange(
                country, start_date, end_date)

        elif filter_type == FilterTypes.day.value:
            start_date = parser.parse(filter_value)
            end_date = start_date + relativedelta(years=+1)

            aggregation = aggregator.getByCountryAndTimerange(
                country, start_date, end_date)

        elif filter_type == FilterTypes.incident_type.value:
            aggregation = aggregator.getByCountryAndType(
                country, filter_value)

        elif filter_type == FilterTypes.company_name.value:
            aggregation = aggregator.getByCountryAndCompany(
                country, filter_value)
        else:
            aggregation = aggregator.getByCountry(country)

        if pagination is not None:
            aggregation = aggregation + pagination.getQuery()

        # print(aggregation)
        # print(list(incidents.aggregate(aggregation)))

        return(list(incidents.aggregate(aggregation)))


class FilterTypes(Enum):
    day = "day"
    month = "month"
    year = "year"
    incident_type = "incident_type"
    company_name = "name"
