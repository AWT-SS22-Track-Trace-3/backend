from tokenize import Token
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Any
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.database.tracking import Tracking
from .database.authentication import Authentication
from .constants import JWT



app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@app.on_event("startup")
async def startup_event():
    print("startup")

@app.on_event("shutdown")
async def shutdown_event():
    print("shutdown")


#<------------------------>
#     Authentification
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
    username: str | None = None
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

class Product(BaseModel):
    name: str
    commonName: Any
    form: str
    strength: str
    drugCode: Any
    packSize: int
    packType: Any
    serialNumber: str
    reimbursmentNumber: Any
    containers: Any
    batchNumber: str
    expiryDate: str
    coding: Any
    marketedStates: Any
    manufacturerName: Any
    manufacturerAdress: Any
    marketingHolderName: Any
    marketingHolderAdress: Any
    wholesaler: Any

@app.post("/create")
async def create(product: Product, user: User = Depends(authenticate)):
    return Tracking.createProduct(product)

class CheckoutBody(BaseModel):
    transactionDate: str
    shipmentDate: str
    Owner: str
    OwnerAddress: str
    futureOwner: str
    futureOwnerAddress: str

@app.post("/checkout")
async def checkout(body: CheckoutBody, user: User = Depends(authenticate)):
    return Tracking.checkoutProduct(body)

class CheckinBody(BaseModel):
    transactionDate: str
    shipmentDate: str
    prevOwner: str
    prevOwnerAddress: str
    Owner: str
    OwnerAddress: str

@app.post("/checkin")
async def checkin(body: CheckinBody, user: User = Depends(authenticate)):
    return Tracking.checkinProduct(body)

@app.get("/terminate/{serialNumber}")
async def terminate(serialNumber: str, user: User = Depends(authenticate)):
    return Tracking.terminateProduct()
