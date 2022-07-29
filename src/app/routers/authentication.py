from os import access
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, status, Response, Cookie
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from jose import JWTError, jwt
from tokenize import Token

from ..database.authentication import Authentication
from ..database.models.models import User, TokenModel
from ..constants import JWT


# Definition - access_lvl
# 0 Wholesaler, can checkin, checkout, and view associated products
# 1 Consumer, can checkin, terminate, and view associated products
# 2 Manufacturer, can create, checkout, and view associated products
# 3 Authorities, can signup users and view everything
# 4 Admin, has admin access


router = APIRouter(
    tags=["authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# <------------------------>
#     Authentication
#<------------------------>

class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str
    access_lvl: int

def create_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + \
        relativedelta(minutes=JWT['ACCESS_TOKEN_EXPIRE_MINUTES'])
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, JWT['SECRET_KEY'], algorithm=JWT['ALGORITHM'])

def create_refresh_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=JWT['REFRESH_TOKEN_EXPIRE_MINUTES'])
    to_encode.update({ "exp": expire })

    return jwt.encode(to_encode, JWT['SECRET_REFRESH_KEY'], algorithm=JWT['ALGORITHM'])

@router.post("/token", response_model=Token)
async def token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user_info = Authentication.is_user(form_data.username, form_data.password)
    if not user_info[0]:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password!")

    access_token = create_token({"sub": form_data.username})
    refresh_token = create_refresh_token({ "sub": form_data.username })
    access_lvl = user_info[1]

    response.set_cookie(key="access_token", value=access_token)
    response.set_cookie(key="refresh_token", value=refresh_token)
    response.set_cookie(key="access_lvl", value=access_lvl)

    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "access_lvl": access_lvl}


async def authenticate(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token, JWT['SECRET_KEY'], algorithms=JWT['ALGORITHM'])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user: User = Authentication.get_user(username)
    if user is None:
        raise credentials_exception
    return user

async def authenticate_refresh(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, JWT['SECRET_REFRESH_KEY'], algorithms=JWT['ALGORITHM'])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user: User = Authentication.get_user(username)
    if user is None:
        raise credentials_exception
    return user

@router.get("/refresh", response_model=Token)
async def refresh(user: User = Depends(authenticate_refresh)):
    return { "access_token": create_token({ "sub": user["username"] }), "token_type": "bearer", "access_lvl": user["access_lvl"] }
