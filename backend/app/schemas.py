from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import List, Optional, Union, Tuple


# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_verified: bool

    class Config:
        from_attributes = True


# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str


# --- Image Schemas ---
class ImageResponse(BaseModel):
    id: int
    filename: str
    created_at: datetime
    is_annotated: bool
    annotation_count: int = 0

    class Config:
        from_attributes = True


# --- Task Schemas ---
class TaskCreate(BaseModel):
    image_ids: List[int]


class TaskResponse(BaseModel):
    id: int
    status: str
    model_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Annotation Schemas ---
class BBoxData(BaseModel):
    type: str = "bbox"
    category_id: int
    category_name: str
    x: float = Field(ge=-0.01, le=1.01)
    y: float = Field(ge=-0.01, le=1.01)
    w: float = Field(ge=0.0, le=1.01)
    h: float = Field(ge=0.0, le=1.01)


class PolygonData(BaseModel):
    type: str = "polygon"
    category_id: int
    category_name: str
    points: List[Tuple[float, float]]

    @field_validator("points")
    def validate_points(cls, v):
        if len(v) < 3:
            raise ValueError("Polygon must have at least 3 points")
        for x, y in v:
            if not (-0.01 <= x <= 1.01 and -0.01 <= y <= 1.01):
                raise ValueError("Polygon coordinates must be between 0 and 1")
        return v


AnnotationItem = Union[BBoxData, PolygonData]


class AnnotationsUpdate(BaseModel):
    annotations: List[AnnotationItem]


class AnnotationsResponse(BaseModel):
    annotations: List[dict]


# --- Category Schemas ---
class CategoryTreeItem(BaseModel):
    id: int
    name: str
    type: str
    children: List[str]
