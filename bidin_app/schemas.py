from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional
from pydantic import ConfigDict

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_staff: bool = False

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# AutoPlate schemas
class AutoPlateCreate(BaseModel):
    plate_number: str = Field(..., max_length=10)
    description: str
    deadline: datetime

    @field_validator("deadline")
    def deadline_must_be_future(cls, v):
        if v <= datetime.now():
            raise ValueError("Deadline must be in the future")
        return v

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for Pydantic v2

class AutoPlateResponse(BaseModel):
    id: int
    plate_number: str
    description: str
    deadline: datetime
    is_active: bool
    created_by_id: int

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for Pydantic v2

class AutoPlateDetailResponse(BaseModel):
    id: int
    plate_number: str
    description: str
    deadline: datetime
    is_active: bool
    bids: List[dict]

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for Pydantic v2

class BidCreate(BaseModel):
    amount: float = Field(..., gt=0)
    plate_id: int

class BidResponse(BaseModel):
    id: int
    amount: float
    plate_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for Pydantic v2