from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any

from database import DB

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
async def create(product: Product):
    DB.createProduct(product)

class CheckoutBody(BaseModel):
    transactionDate: str
    shipmentDate: str
    Owner: str
    OwnerAddress: str
    futureOwner: str
    futureOwnerAddress: str

@app.post("/checkout")
async def checkout(body: CheckoutBody):
    DB.checkoutProduct(body)

class CheckinBody(BaseModel):
    transactionDate: str
    shipmentDate: str
    prevOwner: str
    prevOwnerAddress: str
    Owner: str
    OwnerAddress: str

@app.post("/checkin")
async def checkin(body: CheckinBody):
    DB.checkinProduct(body)

@app.get("/terminate")
async def terminate():
    DB.terminateProduct()
