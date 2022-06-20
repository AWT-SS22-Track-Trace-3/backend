from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Any

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
    if user.access_lvl != 3 and user.access_lvl != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization level!")

    return Authentication.is_username(username)

class New_User(BaseModel):
    username: str
    password: str
    company: str
    address: str
    access_lvl: int

@router.post("/signup")
async def signup(new_user: New_User, user: User = Depends(authenticate)):
    if user.access_lvl != 3 and user.access_lvl != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization level!")

    return Authentication.signup(new_user)
