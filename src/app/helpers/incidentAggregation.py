from typing import Optional
from bson import ObjectId
from datetime import datetime, timedelta
from .aggregation_provider import AggregationPipelineBuilder


class IncidentAggregator:
    builder = None

    def __init__(self, incidents_coll, products_coll, users_coll):
        self.incidents_coll = incidents_coll
        self.products_coll = products_coll
        self.users_coll = users_coll

        self.builder = None

    def _prepareBase(self, match):
        self.builder = AggregationPipelineBuilder().init(match).addLookup(
            self.products_coll, "product", "serial_number", "product", True).addFields(
                "reported_at", {"$arrayElemAt": ["$product.supply_chain", "$chain_step"]}).addLookup(
                    self.users_coll, "reported_at.owner", "username", "assigned_company", True)

    def _matchId(self, oid: ObjectId):
        return {
            "_id": str(oid)
        }

    def _matchAll(self):
        return {
            "_id": {
                "$exists": True
            }
        }

    def _matchCountry(self, country):
        if country != "all":
            return {
                "assigned_company.address.country": country
            }

        return {
            "assigned_company.address.country": {
                "$exists": True
            }
        }

    def _sortByTime(self, order=1):
        return {
            "reporter.timestamp": order,
            "assigned_company.username": order,
            "incident_type": order
        }

    def _standardProjectionSet(self):
        return [
            "_id",
            "reported_at",
            "product._id",
            "product.manufacturers._id",
            "product.manufacturers.password",
            "product.manufacturers.access_lvl",
            "assigned_company._id",
            "assigned_company.password",
            "assigned_company.access_lvl"]

    def getAll(self):
        self._prepareBase(self._matchAll())
        self.builder.addLookup(self.users_coll, "product.manufacturers",
                               "username", "product.manufacturers", False)

        return self.builder.build()

    def getById(self, oid: ObjectId):
        self._prepareBase(self._matchId(oid))
        self.builder.addLookup(self.users_coll, "product.manufacturers",
                               "username", "product.manufacturers", False)

        return self.builder.build()

    def getCountryIncidences(self):
        self._prepareBase(self._matchAll())
        self.builder.addGroup(
            {
                "_id": "$assigned_company.address.country",
                "count": {
                    "$sum": 1
                }
            }
        )

        return self.builder.build()

    def getByCountry(self, country):
        self._prepareCustomPostMatch(self._matchCountry(country))
        self.builder.addSort(self._sortByTime(-1)).addBinaryProjection(
            self._standardProjectionSet(), 0)

        return self.builder.build()

    #TODO: test
    def getByTimestamp(self, timestamp):
        return self.getByCustomPreMatch({
            "reporter.timestamp": datetime.fromtimestamp(timestamp)
        })

    # TODO test against mongodb
    def getByCountryAndTimerange(self, country, start_date, end_date):
        self._prepareCustomPreMatch({
            "reporter.timestamp": {
                "$gte": start_date,
                "$lt": end_date
            }
        })

        self.builder.addMatch(self._matchCountry(country)).addSort(self._sortByTime(-1)).addBinaryProjection(
            self._standardProjectionSet(), 0)

        return self.builder.build()

    def getByCountryAndType(self, country, type):
        self._prepareCustomPreMatch({
            "type": type
        })
        self.builder.addMatch(self._matchCountry(country)).addSort(self._sortByTime(-1)).addBinaryProjection(
            self._standardProjectionSet(), 0)

        return self.builder.build()

    def getByCountryAndCompany(self, country, company):
        self._prepareCustomPostMatch({
            "assigned_company.address.country": country,
            "assigned_company.username": company
        })

        self.builder.addSort(self._sortByTime(-1)).addBinaryProjection(
            self._standardProjectionSet(), 0)

        return self.builder.build()

    def _prepareCustomPreMatch(self, match):
        self._prepareBase(match)

        self.builder.addLookup(self.users_coll, "product.manufacturers",
                               "username", "product.manufacturers", False)

    def _prepareCustomPostMatch(self, match):
        self._prepareBase(self._matchAll())

        self.builder.addMatch(match).addLookup(
            self.users_coll, "product.manufacturers", "username", "product.manufacturers", False)
