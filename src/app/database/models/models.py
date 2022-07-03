from pydantic import BaseModel

class Address(BaseModel):
    street: str
    number: str
    zip_code: str
    city: str
    country: str

class User(BaseModel):
    username: str
    password: str
    company: str
    country: str
    address: Address
    access_lvl: int