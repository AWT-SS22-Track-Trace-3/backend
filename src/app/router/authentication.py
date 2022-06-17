from tokenize import Token
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Any
from jose import JWTError, jwt
from datetime import datetime, timedelta

from ..database.authentication import Authentication
from ..constants import JWT



# Definition - access_lvl
        # 0 Wholesaler, can checkin, checkout, and view associated products
        # 1 Consumer, can checkin, terminate, and view associated products
        # 2 Manufacturer, can create, checkout, and view associated products
        # 3 Authorities, can signup users and view everything
        # 4 Admin, has admin access



router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



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

@router.post("/token", response_model=Token, tags=["authentication"])
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
