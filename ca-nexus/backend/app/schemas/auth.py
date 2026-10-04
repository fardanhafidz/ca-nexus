from pydantic import BaseModel, EmailStr, Field
from typing import Literal

Role = Literal["super_admin", "admin", "user"]
AccountStatus = Literal["pending", "approved", "rejected", "disabled"]
DivisionName = Literal[
    "Mechanical", "Electrical & Instrumentation",
    "Process / Operations", "HSE & Reliability",
]


class RegisterIn(BaseModel):
    full_name: str = Field(min_length=3, max_length=200)
    employee_id: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    division_requested: DivisionName


class LoginIn(BaseModel):
    employee_id: str | None = None
    email: EmailStr | None = None
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    full_name: str
    employee_id: str
    email: str
    role: str
    division: str
    status: str
