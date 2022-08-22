from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

from .authentication import User, authenticate
from ..database.incidents import Incidents
from ..database.tracking import Tracking
from ..database.models.models import NewProduct, ProductCheckin, ProductCheckout
from ..database.models.http_responses import *


# Definition - access_lvl
# 0 Wholesaler, can checkin, checkout, and view associated products
# 1 Consumer, can checkin, terminate, and view associated products
# 2 Manufacturer, can create, checkout, and view associated products
# 3 Authorities, can signup users and view everything
# 4 Admin, has admin access


router = APIRouter(
    tags=["tracking"]
)


# <------------------------>
#    API-Track_Products
# <------------------------>

@router.post("/products/create", responses={**default_responses, 400: {"model": ModelMessage}})
async def create(product: NewProduct, user: User = Depends(authenticate)):
    """
    Post a new product to the database. Products can only be registered by manufacturers and administrators.
    """

    if user["access_lvl"] != 2 and user["access_lvl"] != 4:
        return JSONResponse(status_code=403, content={"message": "Insufficient authorization"})
    result = Tracking.create_product(product.dict(), user)
    if result is False:
        Incidents.report({
            "type": "invalid_create",
            "product": product["product"],
            "description": "Error inserting new product.",
            "chain_step": 0,
            "reporter": {
                "user": user["username"],
                "timestamp": datetime.now()
            }
        })
        return JSONResponse(status_code=400, content={"message": "Error in system, product already exists. Please contact authorities."})
    return JSONResponse(status_code=200, content={"acknowledged": result})


@router.post("/products/{serial_number}/checkout", responses={**default_responses, 400: {"model": ModelMessage}})
async def checkout(body: ProductCheckout, serial_number: str, user: User = Depends(authenticate)):
    """
    Checkout a product. Can only be used by manufacturers, wholesalers, repackagers and administrators.
    """

    if user["access_lvl"] != 0 and user["access_lvl"] != 2 and user["access_lvl"] != 4:
        return JSONResponse(status_code=403, content={"message": "Insufficient authorization"})
    result = Tracking.checkout_product(
        serial_number, body.dict(), user["username"])
    if result["result"] is False:
        Incidents.report({
            "type": "invalid_checkout",
            "product": serial_number,
            "description": "Error checking out product.",
            "chain_step": result["chain_step"],
            "reporter": {
                "user": user["username"],
                "timestamp": datetime.now()
            }
        })
        return JSONResponse(status_code=400, content={"message": "Error in system, please contact authorities."})
    return JSONResponse(status_code=200, content={"acknowledged": result})


@router.post("/products/{serial_number}/checkin", responses={**default_responses, 400: {"model": ModelMessage}})
async def checkin(body: ProductCheckin, serial_number: str, user: User = Depends(authenticate)):
    """
    Checkin a product. Can only be used by wholesalers, repackagers, dispensers and administrators.
    """

    if user["access_lvl"] != 0 and user["access_lvl"] != 1 and user["access_lvl"] != 4:
        return JSONResponse(status_code=403, content={"message": "Insufficient authorization"})
    result = Tracking.checkin_product(
        serial_number, body.dict(), user["username"])
    if result["result"] is False:
        Incidents.report({
            "type": "invalid_checkin",
            "product": serial_number,
            "description": "Error checking in product.",
            "chain_step": result["chain_step"],
            "reporter": {
                "user": user["username"],
                "timestamp": datetime.now()
            }
        })
        return JSONResponse(status_code=400, content={"message": "Error in system, please contact authorities."})
    return JSONResponse(status_code=200, content={"acknowledged": result})


class TerminateBody(BaseModel):
    serial_number: str


@router.put("/products/{serial_number}/terminate", responses={**default_responses, 400: {"model": ModelMessage}})
async def terminate(body: TerminateBody, serial_number: str, user: User = Depends(authenticate)):
    """
    Terminate a product to indicate it successful administration/sell-off. Can only be used dispensers and administrators.
    """

    if user["access_lvl"] != 1 and user["access_lvl"] != 4:
        return JSONResponse(status_code=403, content={"message": "Insufficient authorization"})

    result = Tracking.terminate_product(serial_number)
    if result is False:
        Incidents.report({
            "type": "terminate",
            "information": body.serial_number,
            "user": user
        })
        return JSONResponse(status_code=400, content={"message": "Error in system, please contact authorities."})
    return JSONResponse(status_code=200, content={"acknowledged": result})
