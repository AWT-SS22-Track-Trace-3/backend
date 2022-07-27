from enum import Enum
from pydantic import BaseModel
from datetime import (datetime, date)
from typing import (Any, List, Optional)


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
    type: str
    transaction_date: date
    date_shipped: date
    date_received: date
    owner: str
    future_owner: str = None
    checked_out: bool
    checked_in: bool


class _Supplier(BaseModel):
    transaction_date: str | datetime
    owner: str


class _ShipmentModel(BaseModel):
    date: str | datetime
    shipment_method: str
    tracking_number: str
    handler: str


class IncidentFilter(BaseModel):
    filter_type: str
    filter_value: str | datetime
    interval: Optional[str] = None


class TokenModel(BaseModel):
    access_token: str
    token_type: str
    access_lvl: int


class NewUser(BaseModel):
    username: str
    password: str
    company: str
    country: str
    address: _Address
    type: str


class User(BaseModel):
    username: str
    password: str
    company: str
    country: str
    address: _Address
    type: str
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
    reported: bool
    manufacturer_names: str = None
    manufacturer_adresses: str = None
    marketing_holder_name: str = None
    marketing_holder_adress: str = None
    wholesaler: str = None


class ProductCheckin(BaseModel):
    transaction_date: str | datetime
    shipment_date: str | datetime


class ProductCheckout(BaseModel):
    future_owner: str
    transaction_date: str | datetime
    shipment: _ShipmentModel


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

# 0 Wholesaler, can checkin, checkout, and view associated products
# 1 Consumer, can checkin, terminate, and view associated products
# 2 Manufacturer, can create, checkout, and view associated products
# 3 Authorities, can signup users and view everything
# 4 Admin, has admin access


class AccessLevels(Enum):
    wholesaler = 0
    repackager = 0
    postal_service = 0
    dispenser = 1
    manufacturer = 2
    authority = 3
    admin = 4
