from pycountry import countries
from dateutil import parser
from dateutil.relativedelta import *
from enum import Enum

from app.helpers.incidentGrouper import IncidentGrouper

from ..constants import *
from .models.models import Incident
from .init import client
from .tracking import Tracking
from app.helpers.group_definitions import FormattingTypes, SortingOrder, group_def
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
        group_definition = None

        if(country != "all"):

            group_definition = group_def[group]
            group_query = IncidentGrouper(group_definition)

            aggregation = aggregator.getCountrySummary(
                country, group_query.get_grouping_query(SortingOrder[sort].value))

        else:
            aggregation = aggregator.getCountryIncidences()

        if pagination is not None:
            aggregation = aggregation + pagination.getQuery()

        # print(aggregation)

        # print(list(incidents.aggregate(aggregation)))
        result = list(incidents.aggregate(aggregation))[0]

        if not group_definition is None and group_definition["formatting"]["type"] == FormattingTypes.post_aggregation:
            return Incidents._formatResult(result, group_definition["formatting"])

        return result

    def _formatResult(result, definition):
       # print(definition)
        for item in result["data"]:
            item = definition["fn"](item, definition["format"])

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

        return(list(incidents.aggregate(aggregation))[0])


class FilterTypes(Enum):
    day = "day"
    month = "month"
    year = "year"
    incident_type = "incident_type"
    company_name = "name"
