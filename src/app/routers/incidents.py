from optparse import Option
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import json

from .authentication import User, authenticate
from ..database.incidents import Incidents
from ..database.models.models import Incident, IncidentFilter
from ..database.models.http_responses import *
from ..helpers.pagination import Pagination


# Definition - access_lvl
# 0 Wholesaler, can checkin, checkout, and view associated products
# 1 Consumer, can checkin, terminate, and view associated products
# 2 Manufacturer, can create, checkout, and view associated products
# 3 Authorities, can signup users and view everything
# 4 Admin, has admin access


router = APIRouter(
    tags=["incidents"]
)


# <------------------------>
#    API-Report_Incidents
# <------------------------>


@router.post("/incident", responses=default_responses)
async def incident(report_incident: Incident, user: User = Depends(authenticate)):
    """
    Post a new incident. 
    """
    report_incident = report_incident.dict()
    incident = {
        "type": report_incident["type"],
        "description": report_incident["description"],
        "product": report_incident["product"],
        "chain_step": report_incident["chain_step"],
        "reporter": {
            "timestamp": datetime.now(),
            "user": user["username"]
        }
    }
    acknowledged = Incidents.report(incident)
    return JSONResponse(status_code=200, content={"acknowledged": acknowledged})

incident_summary_response={
    **unauth_response,
    200: {
        "content": {
            "application/json": {
                "example": {
                    "data": [{
                        "_id": {
                            "year": 2022,
                            "day": 254,
                            "formatted": "11.09.2022",
                            "raw": "2022-09-11T00:00:00Z"
                        },
                        "count": 1,
                        "unique_companies": 1.0
                    }]
                }
            }
        }
    }
}


@router.get("/incidents/summary/{country}", responses=incident_summary_response)
async def getIncidentSummary(
        country: str = "all",
        group: Optional[str] = "day",
        sort: Optional[str] = "asc",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        user: User = Depends(authenticate)):
    """
    Get incident summary gouped by the specified criterion. Information include total incident count and unique companies involved.
    Query parameters: 'country' expects the Alpha-2 ID of the requested country (e.g. 'DE' or 'GB'). Passing 'all' will return a summary over all countries.
    'group' expects the group type. Valid group types are: 'day', 'month', 'year', 'company_name', 'incident_type'.
    'sort' specifies the sorting roder of returned result. Valid values are 'asc' (ascending) and 'dsc' (descending).
    'limit' and 'offset' can be used for pagination.
    """

    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        return JSONResponse(status_code=403, content={"message": "Insufficient authorization"})

    pagination = Pagination(limit, offset)

    return Incidents.getGroupedIncidents(country, group, sort, pagination)

# Get all incidents for a specific group key (like month 7) and country but enable pass-around values:
# Get all incidents for one country with group = None, Get all incidents with country = None and group = None etc.

incident_response={
    **unauth_response,
    200: {
        "content": {
            "application/json": {
                "example": {"data":[{"type":"shipment_rejected","name":"Shipment Rejected","product":{},"description":"Received wrong number of packages.","chain_step":10,"reporter":{"user":"admin","timestamp":"2022-10-17T23:24:56.135000"},"assigned_company":{}}],"total":{"count":1}}
            }
        }
    }
}

@router.get("/incidents/{country}", responses=incident_response)
async def getIncidents(
    filter_type: str = None,
    filter_value: str = None,
    country: Optional[str] = "all",
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    user: User = Depends(authenticate)
):
    """
    Get incidents of one country for a filter specification. Query parameters: 'country' expects the Alpha-2 ID of the requested country (e.g. 'DE' or 'GB'). Passing 'all' will return all incidents.
    'filter_type' expects the filter type. Valid filter types are: 'day', 'month', 'year', 'company_name', 'incident_type'.
    'filter_value' expects the value the results should be filtered by. Date filter types always expect a full UTC date string as filter value. E.g. 'filter_type=day&filter_value=2022-10-17T00:00:00Z'.
    'limit' and 'offset' can be used for pagination.
    """
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        return JSONResponse(status_code=403, content={"message": "Insufficient authorization"})

    pagination = Pagination(limit, offset)

    return Incidents.getIncidents(country, filter_type, filter_value, pagination)


@router.get("/heatmap", responses=unauth_response)
async def heatmap(user: User = Depends(authenticate)):
    """
    [deprecated], replaced by /incidents/summary/all
    """
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        return JSONResponse(status_code=403, content={"message": "Insufficient authorization"})
    return JSONResponse(status_code=200, content={"heatmap_data": Incidents.heatmap_data()})
