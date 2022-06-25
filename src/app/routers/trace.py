from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .authentication import User, authenticate
from ..database.tracing import Tracing



# Definition - access_lvl
        # 0 Wholesaler, can checkin, checkout, and view associated products
        # 1 Consumer, can checkin, terminate, and view associated products
        # 2 Manufacturer, can create, checkout, and view associated products
        # 3 Authorities, can signup users and view everything
        # 4 Admin, has admin access



router = APIRouter(
    tags=["tracing"]
)



#<------------------------>
#    API-Trace_Products
#<------------------------>

class Query(BaseModel):
    query: str

@router.post("/search")
async def search(query: Query, user: User = Depends(authenticate)):
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    result = Tracing.search(query)
    if result is None:
        raise HTTPException(status_code=400)
    return result

@router.get("/defined_search")
async def defined_search(user: User = Depends(authenticate)):
    return { "result": "None" }
