from optparse import Option
from fastapi import APIRouter, HTTPException, Depends
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


@router.get("/incidents/summary/{country}", responses=unauth_response)
async def getIncidentSummary(
        country: str = "all",
        group: Optional[str] = "day",
        sort: Optional[str] = "asc",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        user: User = Depends(authenticate)):
"""
Get incident summary gouped by the specified criterion. Information include total incident count and unique companies involved.
Setting country to 'all' will group be country.
"""

    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        return JSONResponse(status_code=403, content={"message": "Insufficient authorization"})

    pagination = Pagination(limit, offset)

    return JSONResponse(status_code=200, content=Incidents.getGroupedIncidents(country, group, sort, pagination))

# Get all incidents for a specific group key (like month 7) and country but enable pass-around values:
# Get all incidents for one country with group = None, Get all incidents with country = None and group = None etc.


@router.get("/incidents/{country}", responses=unauth_response)
async def getIncidents(
    filter_type: str = None,
    filter_value: str = None,
    country: Optional[str] = "all",
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    user: User = Depends(authenticate)
):
"""
Get incidents of one country for a filter specification. Filter type can be any from ["company", "incident_type", "day", "month", "year"]
with the according filter value. Filter values for day, month and year must be valid ISO date strings.
"""
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        return JSONResponse(status_code=403, content={"message": "Insufficient authorization"})

    pagination = Pagination(limit, offset)

    return JSONResponse(status_code=200, content=Incidents.getIncidents(country, filter_type, filter_value, pagination))


@router.get("/heatmap", responses=unauth_response)
async def heatmap(user: User = Depends(authenticate)):
    """
    (deprecated)
    """
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        return JSONResponse(status_code=403, content={"message": "Insufficient authorization"})
    return JSONResponse(status_code=200, content={"heatmap_data": Incidents.heatmap_data()})
