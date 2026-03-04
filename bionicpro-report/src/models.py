from datetime import datetime
from pydantic import BaseModel


class CurrentUser(BaseModel):
    email: str


class UserReport(BaseModel):
    email: str
    country: str | None = None
    prosthesis_total: int
    prosthesis_active: int
    updated_at: datetime
