from tokenize import Token
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Any
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.database.incidents import Incidents

from app.database.tracking import Tracking
from ..database.authentication import Authentication
from ..database.incidents import Incidents
from ..constants import JWT
from authentication import User, authenticate



# Definition - access_lvl
        # 0 Wholesaler, can checkin, checkout, and view associated products
        # 1 Consumer, can checkin, terminate, and view associated products
        # 2 Manufacturer, can create, checkout, and view associated products
        # 3 Authorities, can signup users and view everything
        # 4 Admin, has admin access



router = APIRouter()



#<------------------------>
#    API-Track_Products
#<------------------------>

class Product(BaseModel):
    name: str
    common_name: Any
    form: str
    strength: str
    drug_code: Any
    pack_size: int
    pack_type: Any
    serial_number: str
    reimbursment_number: Any
    containers: Any
    batch_number: str
    expiry_date: str
    coding: Any
    marketed_states: Any
    manufacturer_name: Any
    manufacturer_adress: Any
    marketing_holder_name: Any
    marketing_holder_adress: Any
    wholesaler: Any

@router.post("/create", tags=["tracking"])
async def create(product: Product, user: User = Depends(authenticate)):
    if user.access_lvl != 2 and user.access_lvl != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    result = Tracking.create_product(product, user.username)
    if result is None:
        Incidents.report()
        raise HTTPException(status_code=400, detail="Error in system, please contact authorities.")

    return result

class CheckoutBody(BaseModel):
    transaction_date: str
    shipment_date: str
    owner: str
    owner_address: str
    f_owner: str
    f_owner_address: str

@router.post("/checkout", tags=["tracking"])
async def checkout(body: CheckoutBody, user: User = Depends(authenticate)):
    if user.access_lvl != 0 and user.access_lvl != 2 and user.access_lvl != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    result = Tracking.checkout_product(body)
    if result is None:
        Incidents.report()
        raise HTTPException(status_code=400, detail="Error in system, please contact authorities.")

    return result

class CheckinBody(BaseModel):
    transaction_date: str
    shipment_date: str
    prev_owner: str
    prev_owner_address: str
    owner: str
    owner_address: str

@router.post("/checkin", tags=["tracking"])
async def checkin(body: CheckinBody, user: User = Depends(authenticate)):
    if user.access_lvl != 0 and user.access_lvl != 1 and user.access_lvl != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    result = Tracking.checkin_product(body, user.username)
    if result is None:
        Incidents.report()
        raise HTTPException(status_code=400, detail="Error in system, please contact authorities.")

    return result

@router.get("/terminate/{serial_number}", tags=["tracking"])
async def terminate(serial_number: str, user: User = Depends(authenticate)):
    if user.access_lvl != 1 and user.access_lvl != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    result = Tracking.terminate_product(serial_number)
    if result is None:
        Incidents.report()
        raise HTTPException(status_code=400, detail="Error in system, please contact authorities.")

    return result
