from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Any

from .authentication import User, authenticate
from ..database.incidents import Incidents
from ..database.tracking import Tracking



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


