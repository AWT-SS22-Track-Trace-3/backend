from tokenize import Token
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Any
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.database.incidents import Incidents

from app.database.tracking import Tracking
from .database.authentication import Authentication
from .database.incidents import Incidents
from .constants import JWT



# Definition - access_lvl
        # 0 Wholesaler, can checkin, checkout, and view associated products
        # 1 Consumer, can checkin, terminate, and view associated products
        # 2 Manufacturer, can create, checkout, and view associated products
        # 3 Authorities, can signup users and view everything
        # 4 Admin, has admin access



app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@app.on_event("startup")
async def startup_event():
    print("startup")

@app.on_event("shutdown")
async def shutdown_event():
    print("shutdown")


#<------------------------>
#     Authentication
#<------------------------>

class Token(BaseModel):
    access_token: str
    token_type: str

def create_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=JWT['ACCESS_TOKEN_EXPIRE_MINUTES'])
    to_encode.update({ "exp": expire })

    return jwt.encode(to_encode, JWT['SECRET_KEY'], algorithm=JWT['ALGORITHM'])

@app.post("/token", response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    if not Authentication.is_user(form_data.username, form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password!")
    return { "access_token": create_token({ "sub": form_data.username }), "token_type": "bearer" }

class User(BaseModel):
    username: str
    password: str | None = None 
    company: str | None = None
    address: str | None = None
    access_lvl: int

async def authenticate(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, JWT['SECRET_KEY'], algorithms=JWT['ALGORITHM'])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user: User = Authentication.get_user(username)
    if user is None:
        raise credentials_exception
    return user


#<------------------------>
#           API
#<------------------------>

@app.get("/test/{id}")
async def test(id: int, user: User = Depends(authenticate)):
    print(id)

    return user#{ "message": "Success!" }

            #<------------------------>
            #        API-Login
            #<------------------------>

@app.get("/is_username/{username}")
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

@app.post("/signup")
async def signup(new_user: New_User, user: User = Depends(authenticate)):
    if user.access_lvl != 3 and user.access_lvl != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization level!")

    return Authentication.signup(new_user)

            #<------------------------>
            #        API-Track_Products
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

@app.post("/create")
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

@app.post("/checkout")
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

@app.post("/checkin")
async def checkin(body: CheckinBody, user: User = Depends(authenticate)):
    if user.access_lvl != 0 and user.access_lvl != 1 and user.access_lvl != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    result = Tracking.checkin_product(body, user.username)
    if result is None:
        Incidents.report()
        raise HTTPException(status_code=400, detail="Error in system, please contact authorities.")

    return result

@app.get("/terminate/{serial_number}")
async def terminate(serial_number: str, user: User = Depends(authenticate)):
    if user.access_lvl != 1 and user.access_lvl != 4:
        raise HTTPException(status_code=400, detail="Insufficient authorization")
    result = Tracking.terminate_product(serial_number)
    if result is None:
        Incidents.report()
        raise HTTPException(status_code=400, detail="Error in system, please contact authorities.")

    return result

            #<------------------------>
            #    API-Trace_Products
            #<------------------------>



            #<------------------------>
            #    API-Report_Incidents
            #<------------------------>

            