from optparse import Option
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import json

from .authentication import User, authenticate
from ..database.incidents import Incidents
from ..database.models.models import Incident, IncidentFilter
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


@router.post("/incident")
async def incident(report_incident: Incident, user: User = Depends(authenticate)):
    report_incident = report_incident.dict()
    incident = {
        "type": report_incident["type"],
        "description": report_incident["description"],
        "product": report_incident["product"],
        "chain_step": report_incident["chain_step"],
        "reported": {
            "timestamp": datetime.now(),
            "user": user["username"]
        }
    }
    acknowledged = Incidents.report(incident)
    return {"acknowledged": acknowledged}


@router.get("/incidents/summary/{country}")
async def getIncidentSummary(
        country: str = "all",
        group: Optional[str] = "day",
        sort: Optional[str] = "asc",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        user: User = Depends(authenticate)):

    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        raise HTTPException(
            status_code=400, detail="Insufficient authorization")

    pagination = None
    if limit is not None and offset is not None:
        pagination = Pagination(limit, offset)

    return Incidents.getGroupedIncidents(country, group, sort, pagination)

# Get all incidents for a specific group key (like month 7) and country but enable pass-around values:
# Get all incidents for one country with group = None, Get all incidents with country = None and group = None etc.


@router.get("/incidents/{country}")
async def getIncidents(
    filter_type: str = None,
    filter_value: str = None,
    country: Optional[str] = "all",
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    user: User = Depends(authenticate)
):
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        raise HTTPException(
            status_code=400, detail="Insufficient authorization")

    pagination = None
    if limit is not None and offset is not None:
        pagination = Pagination(limit, offset)

    return Incidents.getIncidents(country, filter_type, filter_value, pagination)


@router.get("/heatmap")
async def heatmap(user: User = Depends(authenticate)):
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        raise HTTPException(
            status_code=400, detail="Insufficient authorization")
    return {"heatmap_data": Incidents.heatmap_data()}
