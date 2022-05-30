from fastapi import FastAPI
import requests as req

from database import db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("startup")

@app.on_event("shutdown")
async def shutdown_event():
    print("shutdown")

@app.get("/test/{id}")
async def test(id):
    print(id)

    return { "message": "Success!" }
    
@app.post("/create")
async def create(product):
    db.postProduct(product)

@app.get("/checkin/{id}")
async def checkin(id):
    db.checkinProduct(id)
    
@app.get("/checkout/{id}")
async def checkout(id):
    db.checkoutProduct(id)

@app.get("/terminate/{id}")
async def terminate(id):
    db.terminateProduct(id)
