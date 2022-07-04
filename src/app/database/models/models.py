from pydantic import BaseModel
from datetime import (datetime, date)
from typing import (Any, List)

class _Address(BaseModel):
    street: str
    number: str
    zip_code: str
    city: str
    country: str

class _Reporter(BaseModel):
    user: str
    timestamp: datetime

class _SupplyChainItem(BaseModel):
    transaction_date: date
    date_shipped: date
    date_received: date
    owner: str
    future_owner: str = None
    checked_out: bool
    checked_in: bool

class _Supplier(BaseModel):
    transaction_date: str
    shipment_date: str
    owner: str

class TokenModel(BaseModel):
    access_token: str
    token_type: str
    access_lvl: int

class User(BaseModel):
    username: str
    password: str
    company: str
    country: str
    address: _Address
    access_lvl: int

class Incident(BaseModel):
    type: str
    product: str
    description: str
    chain_step: int
    reporter: _Reporter = None

class Product(BaseModel):
    name: str
    common_name: str = None
    form: str
    strength: str
    drug_code: str
    pack_size: int
    pack_type: str = None
    serial_number: str
    reimbursment_number: str = None
    containers: int = None
    batch_number: str
    expiry_date: str
    coding: str = None
    marketed_region: str
    manufacturers: List[str]
    sellers: List[str]
    supply_chain: List[_SupplyChainItem]
    manufacturer_names: str = None
    manufacturer_adresses: str = None
    marketing_holder_name: str = None
    marketing_holder_adress: str = None
    wholesaler: str = None

class ProductCheckin(BaseModel):
    product: str
    transaction_date: str
    shipment_date: str

class ProductCheckout(BaseModel):
    product: str
    future_owner: str
    transaction_date: str
    shipment_date: str

class NewProduct(BaseModel):
    name: str
    common_name: str = None
    form: str
    strength: str
    drug_code: str
    pack_size: int
    pack_type: str = None
    serial_number: str
    reimbursment_number: str = None
    containers: int = None
    batch_number: str
    expiry_date: str
    coding: str = None
    marketed_region: str
    manufacturers: List[str] = None
    sellers: List[str] = None
    supplier: _Supplier
    manufacturer_names: str = None
    manufacturer_adresses: str = None
    marketing_holder_name: str = None
    marketing_holder_adress: str = None
    wholesaler: str = None
