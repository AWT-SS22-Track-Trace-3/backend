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
            #    API-Report_Incidents
            #<------------------------>

            
