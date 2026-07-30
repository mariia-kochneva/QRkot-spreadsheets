from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str] = None


class DonationCreate(DonationBase):
    model_config = ConfigDict(extra='forbid')


class DonationDB(DonationBase):
    id: int
    create_date: datetime
    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationDB):
    user_id: Optional[int] = None
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
