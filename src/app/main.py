from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .routers import authentication, incidents, login, trace, track
from .routers.authentication import User, authenticate



app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication.router)
app.include_router(incidents.router)
app.include_router(login.router)
app.include_router(trace.router)
app.include_router(track.router)



@app.on_event("startup")
async def startup_event():
    print("startup")

@app.on_event("shutdown")
async def shutdown_event():
    print("shutdown")


#<------------------------>
#           API
#<------------------------>

# Definition - access_lvl
        # 0 Wholesaler, can checkin, checkout, and view associated products
        # 1 Consumer, can checkin, terminate, and view associated products
        # 2 Manufacturer, can create, checkout, and view associated products
        # 3 Authorities, can signup users and view everything
        # 4 Admin, has admin access

@app.get("/test/{id}")
async def test(id: int, user: User = Depends(authenticate)):
    print(id)

    return user#{ "message": "Success!" }
