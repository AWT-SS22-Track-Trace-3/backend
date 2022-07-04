from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from .authentication import User, authenticate
from ..database.incidents import Incidents
from ..database.tracking import Tracking
from ..database.models.models import NewProduct, ProductCheckin, ProductCheckout



# Definition - access_lvl
        # 0 Wholesaler, can checkin, checkout, and view associated products
        # 1 Consumer, can checkin, terminate, and view associated products
        # 2 Manufacturer, can create, checkout, and view associated products
        # 3 Authorities, can signup users and view everything
        # 4 Admin, has admin access



router = APIRouter(
    tags=["tracking"]
)



#<------------------------>
#    API-Track_Products
#<------------------------>

@router.post("/create")
async def create(product: NewProduct, user: User = Depends(authenticate)):
    if user["access_lvl"] != 2 and user["access_lvl"] != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    result = Tracking.create_product(product.dict(), user)
    if result is False:
        Incidents.report({
            "type": "create",
            "information": product,
            "user": user
        })
        raise HTTPException(status_code=400, detail="Error in system, product already exists. Please contact authorities.")

    return { "acknowledged": result }

class CheckoutBody(BaseModel):
    serial_number: str
    transaction_date: str
    shipment_date: str
    owner: str
    owner_address: str
    f_owner: str
    f_owner_address: str

@router.post("/checkout")
async def checkout(body: ProductCheckout, user: User = Depends(authenticate)):
    if user["access_lvl"] != 0 and user["access_lvl"] != 2 and user["access_lvl"] != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    result = Tracking.checkout_product(body.dict())
    if result is False:
        Incidents.report({
            "type": "create",
            "information": body,
            "user": user
        })
        raise HTTPException(status_code=400, detail="Error in system, please contact authorities.")

    return { "acknowledged": result }

class CheckinBody(BaseModel):
    serial_number: str
    transaction_date: str
    shipment_date: str
    prev_owner: str
    prev_owner_address: str
    owner: str
    owner_address: str

@router.post("/checkin")
async def checkin(body: ProductCheckin, user: User = Depends(authenticate)):
    if user["access_lvl"] != 0 and user["access_lvl"] != 1 and user["access_lvl"] != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    result = Tracking.checkin_product(body.dict(), user["username"])
    if result is False:
        Incidents.report({
            "type": "create",
            "information": body,
            "user": user
        })
        raise HTTPException(status_code=400, detail="Error in system, please contact authorities.")

    return { "acknowledged": result }

class TerminateBody(BaseModel):
    serial_number: str

@router.put("/terminate")
async def terminate(body: TerminateBody, user: User = Depends(authenticate)):
    if user["access_lvl"] != 1 and user["access_lvl"] != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    result = Tracking.terminate_product(body.serial_number)
    if result is False:
        Incidents.report({
            "type": "create",
            "information": body,
            "user": user
        })
        raise HTTPException(status_code=400, detail="Error in system, please contact authorities.")

    return { "acknowledged": result }
