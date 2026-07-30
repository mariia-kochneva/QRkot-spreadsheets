from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from app.core.constants import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH,
    MIN_DESCRIPTION_LENGTH,
)


class CharityProjectBase(BaseModel):
    name: str = Field(
        ..., min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH
    )
    description: str = Field(..., min_length=MIN_DESCRIPTION_LENGTH)
    full_amount: PositiveInt


class CharityProjectCreate(CharityProjectBase):
    model_config = ConfigDict(extra='forbid')


class CharityProjectUpdate(BaseModel):
    name: Optional[str] = Field(
        None, max_length=MAX_NAME_LENGTH, min_length=MIN_NAME_LENGTH
    )
    description: Optional[str] = Field(
        None, min_length=MIN_DESCRIPTION_LENGTH
    )
    full_amount: Optional[PositiveInt] = None
    model_config = ConfigDict(extra='forbid')


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
