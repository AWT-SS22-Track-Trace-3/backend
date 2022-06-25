from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .authentication import User, authenticate
from ..database.incidents import Incidents
from .track import Product



# Definition - access_lvl
        # 0 Wholesaler, can checkin, checkout, and view associated products
        # 1 Consumer, can checkin, terminate, and view associated products
        # 2 Manufacturer, can create, checkout, and view associated products
        # 3 Authorities, can signup users and view everything
        # 4 Admin, has admin access



router = APIRouter(
    tags=["incidents"]
)



#<------------------------>
#    API-Report_Incidents
#<------------------------>

class ReportIncident(BaseModel):
    type: str
    product: Product

@router.post("/incident")
async def incident(report_incident: ReportIncident, user: User = Depends(authenticate)):
    report_incident = report_incident.dict()
    incident = {
        "type": report_incident["type"],
        "product": report_incident["product"],
        "user": user
    }
    result = Incidents.report(incident)
    return { "result": result }

@router.get("/heatmap")
async def heatmap(user: User = Depends(authenticate)):
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    return { "heatmap_data": Incidents.heatmap_data() }
