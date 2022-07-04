from fastapi import APIRouter, HTTPException, Depends
from pycountry import countries
from pydantic import BaseModel

from ..database.authentication import Authentication
from .authentication import User, authenticate



# Definition - access_lvl
        # 0 Wholesaler, can checkin, checkout, and view associated products
        # 1 Consumer, can checkin, terminate, and view associated products
        # 2 Manufacturer, can create, checkout, and view associated products
        # 3 Authorities, can signup users and view everything
        # 4 Admin, has admin access



router = APIRouter(
    tags=["login"]
)



#<------------------------>
#        API-Login
#<------------------------>

@router.get("/is_username/{username}")
async def is_username(username: str, user: User = Depends(authenticate)):
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        raise HTTPException(status_code=403, detail="Insufficient authorization level!")

    return Authentication.is_username(username)

class New_User(BaseModel):
    username: str
    password: str
    company: str
    country: str
    address: str
    access_lvl: int

@router.post("/signup")
async def signup(new_user: New_User, user: User = Depends(authenticate)):
    if user["access_lvl"] != 3 and user["access_lvl"] != 4:
        raise HTTPException(status_code=403, detail="Insufficient authorization level!")

    if countries.get(alpha_2=new_user.country) is None:
        raise HTTPException(status_code=400, detail="Country does not exist!")

    if not Authentication.signup(new_user.dict()):
        raise HTTPException(status_code=406, detail="User already exists!")

    return { "acknowledged": True }
