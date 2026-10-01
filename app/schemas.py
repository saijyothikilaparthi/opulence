from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date
from enum import Enum


class EnquiryType(str, Enum):
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
    CUSTOMIZED = "customized"


class EnquiryCreate(BaseModel):
    enquiry_type: EnquiryType
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=7, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    company_name: Optional[str] = Field(None, max_length=150)
    occasion: Optional[str] = Field(None, max_length=100)
    quantity: Optional[int] = Field(None, ge=1)
    budget: Optional[float] = Field(None, ge=0)
    required_date: Optional[date] = None
    theme: Optional[str] = Field(None, max_length=100)
    customization_details: Optional[str] = None
    file_url: Optional[str] = None

    @field_validator("company_name")
    def validate_corporate_fields(cls, v, info):
        enquiry_type = info.data.get("enquiry_type")
        if enquiry_type == EnquiryType.CORPORATE and not v:
            # Default to "N/A" if company_name not specified so frontend submission succeeds
            return "N/A"
        return v

    @field_validator("quantity")
    def validate_quantity(cls, v, info):
        return v


class EnquiryResponse(BaseModel):
    id: int
    enquiry_type: str
    name: str
    phone: str
    status: str
    message: str


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool


class ProductCreate(BaseModel):
    category_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    category_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_active: bool


class HamperSizeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    max_items: int = Field(..., ge=1)
    description: Optional[str] = None


class HamperSizeResponse(BaseModel):
    id: int
    name: str
    max_items: int
    description: Optional[str] = None
    is_active: bool


class HamperItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(1, ge=1)


class HamperCreate(BaseModel):
    size_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = None
    items: Optional[list[HamperItemCreate]] = None


class HamperResponse(BaseModel):
    id: int
    size_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_active: bool
    items: Optional[list[dict]] = None


class OrderCreate(BaseModel):
    source: Optional[str] = Field("offline", max_length=50) # whatsapp, instagram, offline
    customer_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=7, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    event: Optional[str] = Field(None, max_length=100)
    quantity: Optional[int] = Field(1, ge=1)
    amount: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field("pending", max_length=30)
    payment_status: Optional[str] = Field("unpaid", max_length=30) # unpaid, partial, paid
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    source: str
    customer_name: str
    phone: str
    status: str


class GalleryCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=150)
    image_url: str
    description: Optional[str] = None
