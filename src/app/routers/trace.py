from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import json

from app.database.models.models import AccessLevels

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


# <------------------------>
#    API-Trace_Products
# <------------------------>

class Query(BaseModel):
    query: dict


@router.post("/search")
async def search(query: Query, user: User = Depends(authenticate)):
    """
    Search the product database. The endpoint expects a properly defined '$match'-query according to MongoDB standards to be passed in the request body.
    Users with access level < 3 (authority) will only be returned produtcs, they are directly associated with (restricted search).
    """
    if user["access_lvl"] == AccessLevels.admin.value or user["access_lvl"] == AccessLevels.authority.value:
        result = Tracing.search(query.query)
    else:
        result = Tracing.defined_search(query.query, user["username"])

    if result is None:
        result = []

    return result


@router.get("/product/{serial_number}")
async def getProduct(serial_number, user: User = Depends(authenticate)):
    """
    Get a fully populated product object including manufacturers and supply chain.
    Users with access level < 3 (authority) will only be returned the supply chain up to the point where they last owned the product.
    """
    if user["access_lvl"] == AccessLevels.admin.value or user["access_lvl"] == AccessLevels.authority.value:
        result = Tracing.getProduct(serial_number)
    else:
        result = Tracing.getRestrictedProduct(serial_number, user["username"])
    return result
